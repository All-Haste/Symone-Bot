import os
import logging
import sys
from typing import Dict

from slack_bolt import App

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
)


@app.message("Symone")
def message_hello(message, say):
    say(f"Hey there <@{message['user']}>!")


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 5000)))
