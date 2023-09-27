import logging
import requests
from datetime import datetime, timezone, timedelta
from azure.storage.blob import BlobClient
import jwt
import pytz
import aiohttp


####################### List of API Endpoint #######################

async def GetAuth0Token():    
    connection_string = "DefaultEndpointsProtocol=https;AccountName=sakirsapodprod1;AccountKey=DboIFU/krgaubYtHPXQ92cjhR4rgANVBFPu2pdy46DmMFElO9BpaqcWlyvoHWc0TbDdClfv+NMET+AStYwJx1g==;BlobEndpoint=https://sakirsapodprod1.blob.core.windows.net/;QueueEndpoint=https://sakirsapodprod1.queue.core.windows.net/;TableEndpoint=https://sakirsapodprod1.table.core.windows.net/;FileEndpoint=https://sakirsapodprod1.file.core.windows.net/;"

    # Name of the container and file to download
    container_name = "token"
    file_name = "token_file.txt"

    # Create the BlobClient object
    blob_client = BlobClient.from_connection_string(conn_str=connection_string, container_name=container_name, blob_name=file_name)

    # Download the file as a blob
    downloaded_blob = blob_client.download_blob()

    # Read the contents of the file
    id_token = downloaded_blob.readall().decode('utf-8')

    # logging.info the contents of the file
    logging.info(f"primary token is : {id_token}")

    decoded_token = jwt.decode(id_token, options={"verify_signature": False})
    expiry_time = (datetime.fromtimestamp(decoded_token["exp"]))
    expiry_time_utc = expiry_time.astimezone(pytz.utc)  
    # expiry_time_utc = expiry_time.astimezone()

    time = datetime.now(timezone.utc)

    logging.info(f'\n\ncurrent time is : {time}')

    delta = timedelta(minutes=-2)
    expiry_time_utc = expiry_time_utc + delta
    logging.info(f"\n\nexpiry time of token is : {expiry_time_utc}")

    if expiry_time_utc > time:
        logging.info("expiry_time is greater than the current time.")
        logging.info(f"\n\nfinal token is : {id_token}")

    else:
        logging.info("expiry_time is less than or equal to the current time.")


        tokenAppUrl = "https://sakir-fa-tokenpod-prod1.azurewebsites.net/api/tokenPOD?code=su-aNKxL-1RJ1ir95_DNXhGaRpLGWN8UwOAQdAZUnsbRAzFuMbDqIQ=="
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(tokenAppUrl) as response:
                    logging.info(f"token response status code is : {response.status}")
                    tokenResponse = await response.text()
                    logging.info(f"token response is : {tokenResponse}")
                    id_token = tokenResponse
                    logging.info(f"\n\nfinal token is : {id_token}")
            except aiohttp.ClientError as e:
                logging.info(e)
        

    return id_token