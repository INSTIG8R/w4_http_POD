import csv
import pandas as pd
from .address_extraction import address_extraction
import logging
import json
import tempfile
import os
import aiohttp

async def address_from_croppedImageCSV(id_token, temp_dir):
    authUrl = "https://dev-rtgqet4r.au.auth0.com/oauth/token"
    cityUrl = "https://prod.ecl-miwayne.com/api/Postcodes/City"

    cityHeaders = {
        "Authorization": "Bearer " + id_token
    }

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        try:
            async with session.get(cityUrl, headers=cityHeaders) as response:
                city_list = await response.text()
        except aiohttp.ClientError as e:
            logging.info(e)

    # city_list = json.loads(r.text)
    city_list = [keyword.lower().strip() for keyword in city_list]

    my_cities = ['wiri', 'st johns', 'avonhead', 'waltham', 'harewood', 'albany',
                 'manukau', 'henderson', 'wellington', 'christchurch', 'vanessa', 'rakaia', 'tamaki']
    [city_list.append(city) for city in my_cities if city not in city_list]

    # Create a CSV file for storing extracted addresses in the temp directory
    address_csv_path = os.path.join(temp_dir, 'Address_found.csv')
    with open(address_csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['address_type', 'address'])

    # Read the Cropped_Text.csv from the temp directory
    cropped_text_csv_path = os.path.join(temp_dir, 'Cropped_Text.csv')
    df = pd.read_csv(cropped_text_csv_path)

    for i, row in df.iterrows():
        text = row['Extracted Text']
        s, ad = address_extraction(text)

        if ad != None:
            if any(keyword in ad.lower() for keyword in city_list):
                # if ad != None:
                with open(address_csv_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    if text.strip():
                        writer.writerow([s, ad])

    log = "finised function address_from_croppedImageCSV"

    return log
