import os

from flask import jsonify
from slack.signature import SignatureVerifier

GAME_MASTER = "U72P1S26N"


def verify_signature(request):
    request.get_data()  # Decodes received requests into request.data

    verifier = SignatureVerifier(os.environ['SLACK_SECRET'])

    if not verifier.is_valid_request(request.data, request.headers):
        raise ValueError('Invalid request/credentials.')


def symone_bot(request):
    if request.method != 'POST':
        return 'Only POST requests are accepted', 405

    verify_signature(request)

    response_message = symone_message()
    return jsonify(response_message)


def symone_message():
    message = {
        'response_type': 'in_channel',
        'text': 'Hello',
    }

    return message
