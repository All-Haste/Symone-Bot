import os
from typing import Dict, Callable

from flask import jsonify, Request, Response
from slack_sdk.signature import SignatureVerifier

# This is the ID of the GM user in slack
# TODO: create a proper user permissions system.
GAME_MASTER = os.getenv('GAME_MASTER', "FOO")

MESSAGE_RESPONSE_CHANNEL = "in_channel"
MESSAGE_RESPONSE_EPHEMERAL = "ephemeral"


def verify_signature(request: Request):
    request.get_data()  # Decodes received requests into request.data

    verifier = SignatureVerifier(os.environ["SLACK_SECRET"])

    if not verifier.is_valid_request(request.data, request.headers):
        return Response("Unauthorized", status=401)


def symone_message(slack_data: dict) -> Dict[str, str]:
    input_text = slack_data.get("text")

    if not input_text:
        query = ""
    else:
        query = input_text.lower().replace("+", " ")

    response_callable = response_switch(query)
    message = response_callable()

    return message


def response_switch(query: str) -> Callable:
    switch = {
        "help": help_message,
    }
    return switch.get(query, default_response)


def default_response() -> dict:
    return {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": "I am Symone Bot. I keep track of party gold, XP, and loot. Type `/symone help` to see what I can do."
    }


def help_message() -> dict:
    return {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": """`current xp`: returns current party xp
    `current gold`: returns current party gold
    """,
    }


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
    if request.method != "POST":
        return Response("Only POST requests are accepted", status=405)

    verify_signature(request)

    slack_data = parse_slack_data(request.data)

    response_message = symone_message(slack_data)
    return jsonify(response_message)
