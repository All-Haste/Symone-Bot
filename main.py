import os
import logging
import re
import sys
from typing import Dict

from slack_bolt import App
from slack_bolt.adapter.google_cloud_functions import SlackRequestHandler
from werkzeug import Request

import google.cloud.logging

from symone_bot.aspects import aspect_list
from symone_bot.commands import command_list
from symone_bot.metadata import QueryMetaData
from symone_bot.parser import QueryEvaluator
from symone_bot.response import SymoneResponse

client = google.cloud.logging.Client()
client.setup_logging()

logging.basicConfig(
    format="%(asctime)s\t%(levelname)s\t%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    stream=sys.stdout,
    level=logging.DEBUG,
)


def symone_message(input_text: str, user_id: str) -> Dict[str, str]:
    if user_id is None:
        return {
            "response_type": "ephemeral",
            "text": "Sorry, Slack told me your user ID is blank? That's weird. Please try again.",
        }

    if not input_text:
        query = ""
    else:
        query = input_text.lower()

    evaluator = QueryEvaluator(command_list, aspect_list)
    response = evaluator.parse(query)
    metadata = QueryMetaData(user_id)
    response.metadata = metadata

    return response.get()


app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,
)


@app.message(re.compile("(hi|hello|hey) Symone"))
def message_hello(message, say, context):
    say(f"{context['matches'][0]} there <@{message['user']}>")


@app.message("What can you do Symone?")
def message_help(say):
    help_command = command_list[1]
    say(SymoneResponse(help_command).get())


@app.message(re.compile("Symone, (.*)"))
def aspect_query_handler(message, say, context):
    aspect_candidate = context["matches"][0]
    user_id = message.get("user")

    logging.info(f"Parsing aspect query: {aspect_candidate} from user: {user_id}")

    response = symone_message(aspect_candidate, user_id)
    say(response)


@app.error
def custom_error_handler(error, body, logger):
    logger.exception(f"Error: {error}")
    logger.info(f"Request body: {body}")


def handler(request: Request):
    """
    This is the handler function that is called when an event is
    received from Slack.
    param request: inbound request
    return: response sent to Slack
    """
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(request)
