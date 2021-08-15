import os
import logging
import sys
from typing import Dict, Tuple, Union

from flask import jsonify, Request, Response
from slack_sdk.signature import SignatureVerifier


from symone_bot.aspects import aspect_list
from symone_bot.commands import command_list
from symone_bot.metadata import QueryMetaData
from symone_bot.parser import QueryEvaluator

logging.basicConfig(
    format="%(asctime)s\t%(levelname)s\t%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    stream=sys.stdout,
    level=logging.DEBUG,
)


def verify_signature(request: Request):
    logging.info("Verifying signature of Slack secret.")
    request.get_data()  # Decodes received requests into request.data

    verifier = SignatureVerifier(os.environ["SLACK_SECRET"])

    if not verifier.is_valid_request(request.data, request.headers):
        logging.warning("Provided secret failed verification.")
        return Response("Unauthorized", status=401)


def symone_message(slack_data: dict) -> Dict[str, str]:
    input_text = slack_data.get("text")
    user_id = slack_data.get("user_id")

    if not input_text:
        query = ""
    else:
        query = input_text.lower().replace("+", " ")

    evaluator = QueryEvaluator(command_list, aspect_list)
    response = evaluator.parse(query)
    metadata = QueryMetaData(user_id)
    response.metadata = metadata

    return response.get()


def parse_query(input_text: str) -> Tuple[str, Union[int, None]]:
    query = input_text.lower().split("+")
    # test if final arg is an int
    number_arg = query[-1]
    try:
        number_arg = int(number_arg)
        query = " ".join(query[:-1])
    except ValueError:
        number_arg = None
        query = " ".join(query)
    return query, number_arg


def parse_slack_data(request_body: bytes) -> Dict[str, str]:
    """
    Parses the body data of a request sent from Slack and
    returns it as a dictionary.
    :param request_body: bytes string from request body.
    :return: Dictionary
    """
    data_string = request_body.decode("utf-8")
    pairs = data_string.split("&")
    data = {}
    for pair in pairs:
        key_value = pair.split("=")
        data[key_value[0]] = key_value[1]
    return data


def symone_bot(request: Request) -> Response:
    """
    Primary point of ingress for the bot.
    :param request: inbound request. Note GCP function provides this as a Flask request.
    :return: Flask formatted response.
    """
    if request.method != "POST":
        return Response("Only POST requests are accepted", status=405)

    verify_signature(request)

    slack_data = parse_slack_data(request.data)

    response_message = symone_message(slack_data)
    return jsonify(response_message)
