import pytest

from symone_bot.commands import Command, add, default_response, help_message


def test_command_raises_attribute_error_when_function_not_callable():
    with pytest.raises(AttributeError):
        Command("foo", "bar", "strings aren't callable")


def test_command_help():
    command = Command("foo", "bar", lambda: 1 + 1)
    actual = command.help()
    assert actual == "`foo`: bar."


def test_default_response(test_metadata):
    actual = default_response(test_metadata)
    assert actual["response_type"] == "ephemeral"
    assert actual["text"] == "I'm sorry, I don't understand."


def test_help_message(test_metadata, test_commands):
    actual = help_message(test_metadata)

    assert actual["response_type"] == "ephemeral"
    assert "`help`: retrieves help info.\n" in actual["text"]


@pytest.mark.skip(reason="mocking datastore locally is horrid")
def test_add_deny_unallowed_user(test_metadata, test_aspects):

    aspect = test_aspects[0]
    actual = add(test_metadata, aspect, 100)

    assert actual["response_type"] == "in_channel"
    assert actual["text"] == "Nice try..."


@pytest.mark.skip(reason="mocking datastore locally is horrid")
def test_add(test_metadata, test_aspects, mocker):
    aspect = test_aspects[0]
    aspect.allowed_users = [test_metadata.user_id]

    client_mock = mocker.patch("symone_bot.commands.datastore.Client")

    data_client_stub = DataStoreClientStub()
    result_stub = data_client_stub.query().fetch().next()
    result_stub[aspect.name] = 100

    client_mock.return_value = data_client_stub

    actual = add(test_metadata, aspect, 100)

    assert actual["response_type"] == "in_channel"
    assert actual["text"] == "Updated bar to 200"


class DataStoreClientStub:
    def __init__(self):
        self.query_stub = DataStoreQueryStub()

    def query(self, kind=None):
        return self.query_stub

    def put(self, result):
        pass


class DataStoreQueryStub:
    def __init__(self):
        self.fetch_stub = DataStoreFetchStub()

    def fetch(self):
        return self.fetch_stub

    def key_filter(self, key):
        pass


class DataStoreFetchStub:
    def __init__(self):
        self.result = dict()

    def next(self):
        return self.result
