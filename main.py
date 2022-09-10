import logging
import os
import re
import sys
from typing import Dict

from slack_bolt import App
from slack_bolt.adapter.google_cloud_functions import SlackRequestHandler
from werkzeug import Request

from symone_bot.aspects import aspect_list
from symone_bot.commands import command_list
from symone_bot.handler_source import HandlerSource
from symone_bot.metadata import QueryMetaData
from symone_bot.parser import QueryEvaluator
from symone_bot.response import SymoneResponse

DEPLOYMENT_ENVIRONMENT = os.environ.get("DEPLOYMENT_ENVIRONMENT", "local")

if DEPLOYMENT_ENVIRONMENT == "prod":
    import google.cloud.logging

    client = google.cloud.logging.Client()
    client.setup_logging()

logging.basicConfig(
    format="%(asctime)s\t%(levelname)s\t%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    stream=sys.stdout,
    level=logging.DEBUG,
)


def symone_message(
    input_text: str, user_id: str, handler_source: HandlerSource
) -> Dict[str, str]:
    """
    This is the main function that is called when a message is received from Slack.
    param input_text: text of the message
    param user_id: id of the user who sent the message
    param handler_source: event handler type that called this function
    return: response sent to Slack
    """
    response = {
        "response_type": "ephemeral",
        "text": "Sorry, Slack told me your user ID is blank? That's weird. Please try again.",
    }
    if user_id is None:
        return response

    metadata = QueryMetaData(user_id)

    match handler_source:
        case HandlerSource.HELP:
            response = SymoneResponse(command_list[1], metadata)
        case HandlerSource.ASPECT_QUERY:
            response = run_aspect_query(input_text, metadata)

    return response.get()


def run_aspect_query(input_text, metadata):
    """
    Evaluates the input text as an aspect query and returns a SymoneResponse object..
    """
    if not input_text:
        query = ""
    else:
        query = input_text.lower()
    evaluator = QueryEvaluator(command_list, aspect_list)
    response = evaluator.parse(query)
    response.metadata = metadata
    return response


app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,
)


@app.message(re.compile("(hi|hello|hey) Symone"))
def message_hello(message, say, context):
    """Responds to a user mentioning Symone."""
    say(f"{context['matches'][0]} there <@{message['user']}>")


@app.message(re.compile("(What|what) can you do Symone\\?"))
def message_help(message, say):
    """Help message handler."""
    response = symone_message(
        message.get("text"), message.get("user"), HandlerSource.HELP
    )
    say(response)


@app.message(
    re.compile("(did|Did) we (level up\\?|level up|levelup\\?|levelup|level\\?|level)")
)
def message_did_they_level_up(message, say):
    """Responds to a user asking if they leveled up."""
    original_text = message.get("text")
    "".join([x.upper() if i % 2 else x.lower() for i, x in enumerate(original_text)])
    say(f"\"{original_text}\" :spongebob-mocking:")


@app.message(re.compile("Symone, (.*)"))
def aspect_query_handler(message, say, context):
    """Aspect query handler. Listens for "Symone, <query>"."""
    aspect_candidate = context["matches"][0]
    user_id = message.get("user")

    logging.info(f"Parsing aspect query: {aspect_candidate} from user: {user_id}")

    response = symone_message(aspect_candidate, user_id, HandlerSource.ASPECT_QUERY)
    say(response)


@app.error
def custom_error_handler(error, body, logger):
    logger.exception(f"Error: {error}")
    logger.info(f"Request body: {body}")


def handler(request: Request):
    """
    This is the handler function that is called when an event is
    received from Slack. This is needed to handle Slack inputs for Google Cloud Functions.
    Typically, a slack bot would use the app.start() function to start the server, but for
    cloud functions, SlackRequestHandler is used instead.
    param request: inbound request
    return: response sent to Slack
    """
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(request)
