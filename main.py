import csv
import json
import logging
import uuid

import requests
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(message)s',
    handlers=[
        logging.FileHandler("log.log"),
        logging.StreamHandler()
    ]
)

client = OpenAI(
    api_key="",
)


def format_result(id, verbatim_locality, gpt_result, mindat_result_dict):
    gpt_result["id"] = id
    gpt_result["original_locality"] = verbatim_locality
    if mindat_result_dict and len(mindat_result_dict.get("results")) > 0:
        gpt_result["mindat_id"] = mindat_result_dict.get("results")[0].get("id")
        gpt_result["mindat_text"] = mindat_result_dict.get("results")[0].get("txt")
        gpt_result["mindat_latitude"] = mindat_result_dict.get("results")[0].get("latitude")
        gpt_result["mindat_longitude"] = mindat_result_dict.get("results")[0].get("longitude")
    return gpt_result


def handle_line(row):
    verbatim_location = retrieve_verbatim_location(row)
    logging.info(verbatim_location)
    if verbatim_location is None or verbatim_location == "":
        logging.info(f'Could not determine a verbatim locality for {row[1]}')
        return
    else:
        success = False
        while not success:
            try:
                gpt_result = retrieve_chat_gpt_response(verbatim_location)
                gpt_result_dict = json.loads(gpt_result)
                success = True
            except Exception as e:
                logging.error(f'Error while parsing GPT result for {verbatim_location}', e)
        mindat_result_dict = {}
        if gpt_result_dict.get('locality') is not None and gpt_result_dict.get(
                'locality') != "" and gpt_result_dict.get('locality') != "Undefined":
            mindat_result = requests.get(f'https://api.mindat.org/localities/?txt={gpt_result_dict.get("locality")}&'
                                         f'country={gpt_result_dict.get("country")}',
                                         headers={'Authorization': 'Token'})
            mindat_result_dict = json.loads(mindat_result.content)
            logging.info(mindat_result_dict)
        elif gpt_result_dict.get('municipality') is not None and gpt_result_dict.get('municipality') != "":
            mindat_result = requests.get(
                f'https://api.mindat.org/localities/?txt={gpt_result_dict.get("municipality")}&'
                f'country={gpt_result_dict.get("country")}',
                headers={'Authorization': 'Token'})
            mindat_result_dict = json.loads(mindat_result.content)
            logging.info(mindat_result_dict)
        return format_result(row[0], verbatim_location, gpt_result_dict, mindat_result_dict)


def retrieve_chat_gpt_response(verbatim_location):
    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user",
                   "content": f"""
                       Parse "{verbatim_location}" into json, do not include any explanations, 
                       only provide a  RFC8259 compliant JSON response following this format without deviation.
                       Do not start the response with 'json'. Do not return a list.
                       Translate all values into English. 
                        {{
                       "country": "The country",
                        "municipality": "The municipality",
                        "stateProvince": "The state province",
                        "locality": "The locality"
                        }}
                        If no value can be found always set the field to null."""}],
        temperature=0.1,
    )
    gpt_result = completion.choices[0].message.content
    logging.info(gpt_result)
    if 'json' in gpt_result:
        gpt_result = gpt_result.replace('json', '').replace('`', '').replace('\n', '').strip()
        logging.info('Cleaned result: ' + gpt_result)
    return gpt_result


def retrieve_verbatim_location(row):
    verbatim_location = ''
    for row_index in [38, 41, 42, 43, 44, 45]:
        if row[row_index] is not None and row[row_index] != "":
            if verbatim_location != '':
                verbatim_location = verbatim_location + ", "
            verbatim_location = verbatim_location + row[row_index]
    verbatim_location = verbatim_location.strip()
    if verbatim_location is None or verbatim_location == "":
        verbatim_location = row[47]
    if verbatim_location is None or verbatim_location == "":
        verbatim_location = row[48]
    return verbatim_location


def process_csv(name: str):
    with open(name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        with open(f"csv_result_{uuid.uuid4()}.csv", 'w') as csvoutfile:
            writer = csv.DictWriter(csvoutfile,
                                    fieldnames=["id", "original_locality", "country", "municipality", "stateProvince",
                                                "locality", "mindat_id", "mindat_text", "mindat_latitude",
                                                "mindat_longitude"],
                                    extrasaction='ignore')
            writer.writeheader()
            for i, row in enumerate(spamreader):
                if i == 0:
                    logging.info(', '.join(row))
                else:
                    handle_line(row)


if __name__ == '__main__':
    process_csv("CRS.csv")
