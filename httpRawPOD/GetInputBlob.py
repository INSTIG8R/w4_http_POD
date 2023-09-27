import logging
import requests
from datetime import datetime, timezone, timedelta
from azure.storage.blob import BlobClient
import jwt
import pytz
import aiohttp


####################### List of API Endpoint #######################

def GetInputBlob(inputBlobName):    
    connection_string = "DefaultEndpointsProtocol=https;AccountName=sakirsapodprod1;AccountKey=DboIFU/krgaubYtHPXQ92cjhR4rgANVBFPu2pdy46DmMFElO9BpaqcWlyvoHWc0TbDdClfv+NMET+AStYwJx1g==;BlobEndpoint=https://sakirsapodprod1.blob.core.windows.net/;QueueEndpoint=https://sakirsapodprod1.queue.core.windows.net/;TableEndpoint=https://sakirsapodprod1.table.core.windows.net/;FileEndpoint=https://sakirsapodprod1.file.core.windows.net/;"

    # Name of the container and file to download
    container_name = "rawfiles"
    file_name = inputBlobName

    # Create the BlobClient object
    blob_client = BlobClient.from_connection_string(conn_str=connection_string, container_name=container_name, blob_name=file_name)

    # Download the file as a blob
    myblob = blob_client.download_blob()
        

    return myblob