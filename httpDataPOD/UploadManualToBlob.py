from azure.storage.blob import BlobServiceClient, BlobClient
import logging

# storage_account_key = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
# storage_account_name = "devstoreaccount1"
# connection_string = "AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;DefaultEndpointsProtocol=http;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"
# container_name = "manual"

storage_account_key = "DboIFU/krgaubYtHPXQ92cjhR4rgANVBFPu2pdy46DmMFElO9BpaqcWlyvoHWc0TbDdClfv+NMET+AStYwJx1g=="
storage_account_name = "sakirsapodprod1"
connection_string = "DefaultEndpointsProtocol=https;AccountName=sakirsapodprod1;AccountKey=DboIFU/krgaubYtHPXQ92cjhR4rgANVBFPu2pdy46DmMFElO9BpaqcWlyvoHWc0TbDdClfv+NMET+AStYwJx1g==;BlobEndpoint=https://sakirsapodprod1.blob.core.windows.net/;QueueEndpoint=https://sakirsapodprod1.queue.core.windows.net/;TableEndpoint=https://sakirsapodprod1.table.core.windows.net/;FileEndpoint=https://sakirsapodprod1.file.core.windows.net/;"
container_name = "manual"

def UploadManualToBlob(file_path,file_name):
    # blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_string)
    logging.info(f"\n\nfile name in upload manual to blob: {file_name}")
    blob = BlobClient.from_connection_string(conn_str=connection_string, container_name=container_name, blob_name=file_name)
    # blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    with open(file_path,"rb") as data:
        blob.upload_blob(data,overwrite=True)
        logging.info(f"Uploaded {file_name}.")
        log = "completed function upload manual to blob"
    logging.info(log)

    return log

