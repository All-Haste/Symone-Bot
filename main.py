import os
import logging
import sys
from typing import Dict

from slack_bolt import App
from slack_bolt.adapter.google_cloud_functions import SlackRequestHandler
from werkzeug import Request

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


app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,
)


@app.message("Symone")
def message_hello(message, say):
    say(f"Hey there <@{message['user']}>!")


def handler(request: Request):
    """
    This is the handler function that is called when an event is
    received from Slack.
    param request: inbound request
    return: response sent to Slack
    """
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(request)
