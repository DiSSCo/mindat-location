import csv
import json
import logging
from typing import Dict, Any, List, Union

import requests
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(message)s',
    handlers=[
        logging.FileHandler("log.log"),
        logging.StreamHandler()
    ]
)


def format_result(id: Union[str, int], verbatim_locality: str, mindat_result_dict: Union[Dict[str, Any], None]) -> Dict[
    str, Any]:
    """
    Formats the result of the mindat api call
    :param id:
    :param verbatim_locality:
    :param mindat_result_dict:
    :return:
    """
    result = dict()
    result["id"] = id
    result["original_locality"] = verbatim_locality
    if mindat_result_dict and len(mindat_result_dict.get("results")) > 0:
        result["mindat_id"] = mindat_result_dict.get("results")[0].get("id")
        result["mindat_text"] = mindat_result_dict.get("results")[0].get("txt")
        result["mindat_latitude"] = mindat_result_dict.get("results")[0].get("latitude")
        result["mindat_longitude"] = mindat_result_dict.get("results")[0].get("longitude")
    logging.info(f'Found Mindat location: {str(result.get("mindat_text"))}')
    return result


def handle_line(row: List[str], cml_args: argparse.Namespace) -> Dict[str, Any]:
    """
    Handles a single line in the csv file. Retrieve the location from the CSV and if it is not empty, query the mindat.
    This method should always return a result so that the amount of lines in the resulting file are equal to the processed file.
    :param row: A single row from the CSV file
    :param cml_args: The command line arguments
    :return: Return a dict with the results
    """
    verbatim_location = row[cml_args.location_column]
    if verbatim_location is None or verbatim_location == "":
        return format_result(row[0], "Unable to retrieve verbatim location", None)
    else:
        logging.info(f'Found location: {verbatim_location} in the csv file')
        if verbatim_location is None or verbatim_location == "":
            logging.info(f'Could not determine a verbatim locality for {row[1]}')
        else:
            try:
                mindat_result = requests.get(f'https://api.mindat.org/localities/?txt={verbatim_location}',
                                             headers={'Authorization': f'Token {cml_args.token}'})
                mindat_result_dict = json.loads(mindat_result.content)
                return format_result(row[0], verbatim_location, mindat_result_dict)
            except Exception as e:
                logging.error(f'Could not process {verbatim_location} due to {e}')
                return format_result(row[0], verbatim_location, None)


def process_csv(cml_args: argparse.Namespace) -> None:
    """

    :param cml_args:
    :return:
    """
    with open(cml_args.input, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        with open(cml_args.output, 'w') as csvoutfile:
            writer = csv.DictWriter(csvoutfile,
                                    fieldnames=["id", "original_locality", "mindat_id", "mindat_text",
                                                "mindat_latitude",
                                                "mindat_longitude"],
                                    extrasaction='ignore')
            writer.writeheader()
            for row in reader:
                writer.writerow(handle_line(row, cml_args))


def setup_argument_parser() -> argparse.Namespace:
    """
    Setup the argument parser
    :return: The parsed arguments
    """
    parser = argparse.ArgumentParser(description='Arguments for ')
    parser.add_argument("--input", "-i", type=str, help="The csv file to process", required=True)
    parser.add_argument("--location_column", "-l", type=int,
                        help="The column in which the verbatim location can be found", required=True)
    parser.add_argument('--token', "-t", type=str, help="The token to access the mindat api", required=True)
    parser.add_argument("--output", "-o", type=str, help="The csv file in which the result will be stored",
                        default="result.csv", required=False)
    parser.add_argument("--country_column", "-c", type=int, help="The column in which the country can be found",
                        required=False)
    parser.add_argument("--id_column", "-id", type=int, help="The column in which the id can be found", required=False)
    return parser.parse_args()


if __name__ == '__main__':
    """
    The main function. First sets up cml arguments and the starts processing the csv file
    """
    args = setup_argument_parser()
    process_csv(args)
