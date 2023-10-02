import logging
import base64
import azure.functions as func
import os
import cv2
import csv
import numpy as np
import pytesseract
from PIL import Image
import pandas as pd
import asyncio
import tempfile
import aiohttp

from .clean_image import clean_image
from .cropBoundingBox import cropBoundingBox
from .dateAndCode_extraction import dateAndCode_extraction
from .address_from_croppedImage import address_from_croppedImageCSV
from .values import values
from .create_JSON import create_JSON
from .DeleteFolderContents import DeleteFolderContents
from .UploadManualToBlob import UploadManualToBlob
from .UploadProcessedToBlob import UploadProcessedToBlob
from .UploadManualToMiwayne import UploadManualToMiwayne
from .UploadProcessedToMiwayne import UploadProcessedToMiwayne
from .format_datetime import format_datetime
from .GetAuth0Token import GetAuth0Token
from .GetInputBlob import GetInputBlob


async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')


    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        # inputBlobURL = req_body.get('url')
        inputBlobName = req_body.get('name')
        logging.info(f"input blob name is : {inputBlobName}")


    if inputBlobName:
        for inputBlobName in inputBlobName:
            logging.info("###########################  new function started  ###########################")

            myblob = GetInputBlob(inputBlobName)

            nameWithPath = myblob.name
            fileName = nameWithPath.split("/")[-1]
            fileNameNoExt = fileName.split(".")[:-1]

            # Extract the desired part
            start_index = nameWithPath.rfind('_') + 1
            end_index = nameWithPath.rfind('.')
            id = nameWithPath[start_index:end_index]

            logging.info("filename : " + fileName)

            fileData = myblob.read()
            encoded_string = base64.b64encode(fileData)
            bytes_file = base64.b64decode(encoded_string, validate=True)

            with tempfile.TemporaryDirectory() as temp_dir:
                # Create temporary directories
                tmp_image_dir = os.path.join(temp_dir, 'image')
                os.makedirs(tmp_image_dir, exist_ok=True)

                tmp_cropped_image_dir = os.path.join(temp_dir, 'croppedImage')
                os.makedirs(tmp_cropped_image_dir, exist_ok=True)

                tmp_manual_dir = os.path.join(temp_dir, 'manual')
                os.makedirs(tmp_manual_dir, exist_ok=True)

                tmp_processed_dir = os.path.join(temp_dir, 'processed')
                os.makedirs(tmp_processed_dir, exist_ok=True)

                # Save the blob content to a temporary image file
                tmp_image_path = os.path.join(tmp_image_dir, fileName)
                with open(tmp_image_path, 'wb') as f:
                    f.write(bytes_file)

                confi = r'''
                {
                "OCR": {
                    "ImagePreprocessing": {
                    "Deskew": true,
                    "CorrectOrientation": true,
                    "EnhanceContrast": true,
                    "Binarize": true
                    },
                    "Segmentation": {
                    "Mode": "Paragraph",
                    "Language": "eng",
                    "PageSegMode": "auto"
                    },
                    "Recognition": {
                    "EngineMode": "LSTM_ONLY",
                    "CharWhitelist": "",
                    "CharBlacklist": "",
                    "PSM": "auto",
                    "OEM": "DEFAULT"
                    }
                }
                }
                '''

                id_token = await GetAuth0Token()

                with open(os.path.join(temp_dir, 'TextDetected.csv'), mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Filename', 'Extracted Text'])

                for filename_png in os.listdir(tmp_image_dir):
                    logging.info(f"started working on {filename_png}")
                    if filename_png.endswith('.png'):
                        try:
                            image = cv2.imread(os.path.join(tmp_image_dir, filename_png))
                            cleaned = clean_image(image)
                            text = pytesseract.image_to_string(cleaned, config=confi)

                            with open(os.path.join(temp_dir, 'TextDetected.csv'), mode='a', newline='') as file:
                                writer = csv.writer(file)
                                if text.strip():
                                    writer.writerow([filename_png, text])
                        except:
                            logging.info("Error in Text extraction from whole image.")

                        try:
                            cropBoundingBox_result = cropBoundingBox(cleaned, filename_png, temp_dir)
                            logging.info(cropBoundingBox_result)
                            bounding_box_path = os.path.join(tmp_cropped_image_dir, f"{filename_png[:-4]}_boxes")

                            with open(os.path.join(temp_dir, 'Cropped_Text.csv'), mode='w', newline='') as file:
                                writer = csv.writer(file)
                                writer.writerow(['Filename', 'Extracted Text'])

                            for filename_box in os.listdir(bounding_box_path):
                                if filename_box.endswith('.png'):
                                    image_box = cv2.imread(os.path.join(bounding_box_path, filename_box))
                                    text = pytesseract.image_to_string(image_box, config=confi)
                                    with open(os.path.join(temp_dir, 'Cropped_Text.csv'), mode='a', newline='') as file:
                                        writer = csv.writer(file)
                                        if text.strip():
                                            writer.writerow([filename_box, text])
                        except:
                            logging.info("Couldn't create bounding boxes, tile cannot extend outside image")

                        try:
                            dates, Codes, Times, from_ad, to_ad = '', '', '', None, None
                            whole_page = pd.read_csv(os.path.join(temp_dir, 'TextDetected.csv'))
                            dates, Codes, Times, from_ad, to_ad, uniqueCode = dateAndCode_extraction(whole_page, image, temp_dir)
                            address_from_croppedImageCSV_result = await address_from_croppedImageCSV(id_token, temp_dir)
                            logging.info(address_from_croppedImageCSV_result)

                            date, time, code, fromA, toA, manual = values(
                                dates, Times, Codes, from_ad, to_ad, uniqueCode, os.path.join(temp_dir, 'Address_found.csv'))

                            if not code.strip():
                                manual = True
                                logging.info("ConNote not found")

                            logging.info(f"\n\nDate Time Code:{date},{time},{code}\n"
                                        f"\nSender: {fromA}\n"
                                        f"\nReceiver: {toA}\n"
                                        f"\nManual: {manual}")
                            
                            create_JSON_result = create_JSON(filename_png, date, time, code, fromA, toA, manual)
                            logging.info(create_JSON_result)

                            deliveryDate = format_datetime(date, time)

                            if manual:
                                customerPath = f"manual_{filename_png}.pdf"

                                img = Image.open(os.path.join(tmp_image_dir, filename_png))
                                pdf_filename = os.path.join(tmp_manual_dir, f"manual_{filename_png[:-4]}.pdf")
                                Blobfilename = f'{filename_png[:-4]}.pdf'

                                img.save(pdf_filename, 'PDF', resolution=100.0)
                                logging.info("Manual Version generated")

                                log = UploadManualToBlob(pdf_filename, Blobfilename)
                                logging.info(f"from init py log = {log}")
                                response = await UploadManualToMiwayne(id, code, fromA, toA, deliveryDate, id_token)
                                logging.info(f"miwayne upload from init py = {response}")

                                logging.info("Manual Version uploaded successfully from init")

                            else:
                                logging.info("All Data stripped successfully")

                                customerPath = f"{code}.pdf"
                                img = Image.open(os.path.join(tmp_image_dir, filename_png))
                                pdf_filename = os.path.join(tmp_processed_dir, customerPath)
                                Blobfilename = f'{customerPath}'

                                img.save(pdf_filename, 'PDF', resolution=100.0)

                                log = UploadProcessedToBlob(pdf_filename, Blobfilename)
                                logging.info(f"from init py log = {log}")
                                response = await UploadProcessedToMiwayne(id, code, fromA, toA, deliveryDate, id_token)
                                logging.info(f"miwayne upload from init py = {response}")
                                logging.info(f"{code} Processed Version uploaded successfully from init")

                        except:
                            logging.info("Error in generating Customer Version PDF.")

                            img = Image.open(os.path.join(tmp_image_dir, filename_png))
                            pdf_filename = os.path.join(tmp_manual_dir, f"manual_{filename_png[:-4]}.pdf")
                            Blobfilename = f'{filename_png[:-4]}.pdf'

                            img.save(pdf_filename, 'PDF', resolution=100.0)
                            logging.info("Manual Version generated from except block")

                            log = UploadManualToBlob(pdf_filename, Blobfilename)
                            logging.info(f"from init py log = {log}")
                            response = await UploadManualToMiwayne(id, code, fromA, toA, deliveryDate, id_token)
                            logging.info(f"miwayne upload from init py = {response}")
                            logging.info("Manual Version uploaded successfully from except block in init")

                        logging.info(f"finised working on {filename_png}")

            logging.info(f"completed working on function {fileName}")




            return func.HttpResponse(f"dataRawPOD function executed for input blob name : {inputBlobName}")
    else:
        return func.HttpResponse(
             "Blob URL or Name not found",
             status_code=400
        )
