import logging
import os
import random
import re
import sys

from slack_bolt import App
from slack_bolt.adapter.google_cloud_functions import SlackRequestHandler
from werkzeug import Request

from symone_bot.util import mocking_spongebob_reply
from symone_bot.bot_ingress import symone_message
from symone_bot.handler_source import HandlerSource

DEPLOYMENT_ENVIRONMENT = os.environ.get("DEPLOYMENT_ENVIRONMENT", "local")

if DEPLOYMENT_ENVIRONMENT == "prod":
    import google.cloud.logging

    client = google.cloud.logging.Client()
    client.setup_logging()
    logging.basicConfig(
        format="%(asctime)s\t%(levelname)s\t%(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        stream=sys.stdout,
        level=logging.INFO,
    )
else:
    logging.basicConfig(
        format="%(asctime)s\t%(levelname)s\t%(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        stream=sys.stdout,
        level=logging.DEBUG,
    )

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,
)


@app.message(re.compile("(hi|hello|hey) Symone", re.IGNORECASE))
def message_hello(message, say, context):
    """Responds to a user mentioning Symone."""
    say(f"{context['matches'][0]} there <@{message['user']}>")


@app.message(re.compile("what can you do Symone\\?", re.IGNORECASE))
def message_help(message, say):
    """Help message handler."""
    response = symone_message(
        message.get("text"), message.get("user"), HandlerSource.HELP
    )
    say(response)


@app.message(
    re.compile(
        "Did we (level up\\?|level up|levelup\\?|levelup|level\\?|level)", re.IGNORECASE
    )
)
def message_did_they_level_up(message, say):
    """Responds to a user asking if they leveled up."""
    if bool(random.getrandbits(1)):
        reply = mocking_spongebob_reply(message)
    else:
        reply = "No :arms_crossed:"
    say(reply)


@app.message(re.compile("Symone, (.*)", re.IGNORECASE))
def aspect_query_handler(message, say, context):
    """Aspect query handler. Listens for "Symone, <query>"."""
    aspect_candidate = context["matches"][0]
    user_id = message.get("user")

    logging.info(f"Parsing aspect query: {aspect_candidate} from user: {user_id}")
    response = symone_message(aspect_candidate, user_id, HandlerSource.ASPECT_QUERY)
    say(response)


@app.error
def custom_error_handler(error, body, logger, client, payload):
    logger.exception(f"Error: {error}")
    logger.info(f"Request body: {body}")
    client.chat_postEphemeral(
        channel=payload["channel"],
        user=payload["user"],
        text=f"Sorry, I had an error processing your request. Please try again. {error}",
    )


@app.event("message")
def handle_message_events(body, logger):
    logger.debug(body)


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
