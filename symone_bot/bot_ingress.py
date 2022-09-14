import logging
from typing import Dict

from symone_bot.commands import command_dict
from symone_bot.handler_source import HandlerSource
from symone_bot.metadata import QueryMetaData
from symone_bot.parser import QueryEvaluator
from symone_bot.response import SymoneResponse


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
            response = SymoneResponse(command_dict.get("help"), metadata)
        case HandlerSource.ASPECT_QUERY:
            response = run_aspect_query(input_text, metadata)

    return response.get()


def run_aspect_query(input_text, metadata):
    """
    Evaluates the input text as an aspect query and returns a SymoneResponse object..
    """
    logging.debug(f"run_aspect_query: Received input: {input_text}")
    if not input_text:
        raise ValueError("Input text is empty.")
    evaluator = QueryEvaluator.get_evaluator()
    response = evaluator.parse(input_text)
    response.metadata = metadata
    return response
