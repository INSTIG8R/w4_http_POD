import pandas as pd
import logging 
import re
from datetime import datetime
import csv
from .unique_address import *
import os

def dateAndCode_extraction(df, image, temp_dir):
    # Define the regex pattern to match dates in the format YYYY-MM-DD
    date_pattern = r'\d{2}/\d{2}/\d{4}|\d{1}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}|\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{2}'
    code_pattern = r'ECC[A-Z0-9]{7}|ECW[A-Z0-9]{7}|IFL[0-9]{7}|1FL[0-9]{7}|ILF[0-9]{7}|£CC[A-Z0-9]{7}|—CC[A-Z0-9]{7}|€CC[A-Z0-9]{7}|Ecc[A-Z0-9]{7}|ECc[A-Z0-9]{7}|Ecco[A-Z0-9]{7}|\(FL[0-9]{7}|{FL[0-9]{7}'
    time_pattern = r'[0-9]{2}:[0-9]{2} a.m|[0-9]{2}:[0-9]{2} p.m|[0-9]{1}:[0-9]{2} a.m|[0-9]{1}:[0-9]{2} p.m|[0-9]{1}:[0-9]{2} PM|[0-9]{1}:[0-9]{2} AM|[0-9]{2}:[0-9]{2}'

    sealink_pattern = r'\bSEALINK\b'
    sub60_pattern = r'\bSUB60\b'
    bascik_pattern = r'\bBASCIK\b|\bBASCI\b'
    uniqueCode = ''

    # Create a CSV file for storing extracted dates, codes, and addresses in the temp directory
    date_code_csv_path = os.path.join(temp_dir, 'Date_Code.csv')
    with open(date_code_csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header row to the CSV file
        writer.writerow(['Filename', 'Extracted Date', 'Time',
                         'Extracted Code', 'From Address', 'To Address', 'uniqueCode'])

    # Iterate over each row in the DataFrame and extract information
    for i, row in df.iterrows():
        text = row['Extracted Text']
        dates = re.findall(date_pattern, text)
        codes = re.findall(code_pattern, text)
        times = re.findall(time_pattern, text)
        from_ad, to_ad = None, None  # address_extraction(text)
        filename = row['Filename']

        # Check if sealink company
        is_sealink = bool(re.search(sealink_pattern, text))
        if is_sealink:
            logging.info(f"sealink: {is_sealink}\n")
            from_ad, to_ad = sealink_address(image)

        # Check if sub60 company
        is_sub60 = bool(re.search(sub60_pattern, text))
        if is_sub60:
            logging.info(f"sub60: {is_sub60}\n")
            from_ad, to_ad = sub60(image)

        # Check if bascik company
        is_bascik = bool(re.search(bascik_pattern, text))
        if is_bascik:
            logging.info(f"bascik: {is_bascik}\n" )
            from_ad, to_ad, uniqueCode = bascik(image)

        with open(date_code_csv_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if text.strip():
                writer.writerow(
                    [filename, dates, times, codes, from_ad, to_ad, uniqueCode])

    return dates, codes, times, from_ad, to_ad, uniqueCode
