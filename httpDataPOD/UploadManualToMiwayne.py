import aiohttp
import asyncio
import logging
import json
import aiohttp

async def UploadManualToMiwayne(id, code, fromA, toA, deliveryDate, id_token):
    
    ####################### List of API Endpoint #######################

    # categoryUrl = "https://dev.test-wayne.com/api/DocumentCategories"
    manualPODUrl = "https://prod.ecl-miwayne.com/api/pod/manual"
    configUrl = "https://prod.ecl-miwayne.com/api/UIConfigurations/data/"


    ####################### Obtaining Miwayne Document Type POD Config Data #######################

    configModule = {
        "POD_DOCUMENT_CATEGORY" : "POD DOCUMENT CATEGORY",
        "POD_PROCESSED_CONFIGURATION" : "POD PROCESS CONFIGURATION",
        "POD_RAW_CONFIGURATION" : "POD RAW CONFIGURATION",
        "POD_MANUAL_CONFIGURATION" : "POD MANUAL CONFIGURATION",
        "POD_CUSTOMER_VERSION_CONFIGURATION" : "POD CUSTOMER VERSION CONFIGURATION"
    }

    configType = {
        "DOCUMENT_CATEGORY" : "DOCUMENT CATEGORY"
    }

    podConfigList = configUrl+configModule["POD_DOCUMENT_CATEGORY"]+"/"+configType['DOCUMENT_CATEGORY']
    manualPodConfigList =configUrl+configModule["POD_MANUAL_CONFIGURATION"]+"/"+configType['DOCUMENT_CATEGORY']
    
    categoryHeaders = {
        "Authorization": "Bearer " + id_token
    }

    logging.info("categoryHeaders: {}".format(categoryHeaders))

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        try:
            async with session.get(podConfigList, headers=categoryHeaders) as response:
                podConfigListResponse = await response.text()
        except aiohttp.ClientError as e:
            logging.info(e)

    logging.info("\n\nconfig response: {}".format(podConfigListResponse))

    podConfigListResponse = json.loads(podConfigListResponse)
    podID = podConfigListResponse[0]['id']

    logging.info(f"\n\npodID : {podID}"  )

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        try:
            async with session.get(manualPodConfigList, headers=categoryHeaders) as response:
                manualPodConfigListResponse = await response.text()
        except aiohttp.ClientError as e:
            logging.info(e)


    logging.info("\n\nconfig response: {}".format(manualPodConfigListResponse))

    manualPodConfigListResponse = json.loads(manualPodConfigListResponse)
    manualPodConfigID = manualPodConfigListResponse[0]['id']

    logging.info(f"\n\nmanualPodConfigID : {manualPodConfigID}"  )   
    logging.info(f"\n\n id is :  {id}"
                 f"\n code is : {code}"
                 f"\n sender is : {fromA}"
                 f"\n receiver is : {toA}"
                 f"\n date is : {deliveryDate}")
    payload={
        "id": id,
        "consignmentNote": code,
        "deliveryDate": deliveryDate,
        "senderAddress": fromA,
        "receiverAddress": toA
    }

    headers = {
        'Authorization' : 'Bearer ' + id_token,
        'Content-Type': 'application/json'
    }


    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        try:
            async with session.post(manualPODUrl, headers=headers, json = payload) as response:
                response = await response.text()
        except aiohttp.ClientError as e:
            logging.info(e)

    logging.info(f"\n\nresponse from upload manual to miwayne is : {response}")
    logging.info(f"\n\nuploaded successfully from function")

    return response