def mocking_spongebob_reply(message):
    """
    Returns a mocking spongebob reply.

    param message: message received from Slack
    return: mocking spongebob reply
    """
    original_text = message.get("text")
    mocking_text = "".join(
        [x.lower() if i % 2 else x.upper() for i, x in enumerate(original_text)]
    )
    reply = f':spongebob-mocking: "{mocking_text}" :spongebob-mocking:'
    return reply
