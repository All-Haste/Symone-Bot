import pytest

from symone_bot.data import DatabaseClient


def test_create_client(mocker):
    datastore_mock = mocker.patch("symone_bot.data.datastore", autospec=True)
    DatabaseClient("test-project")

    datastore_mock.Client.assert_called_once_with("test-project")


@pytest.mark.skip(reason="This test needs the datastore emulator running")
def test_get_current_campaign_id():
    client = DatabaseClient("test-project")
    current_campaign_id = client.get_current_campaign_entity()

    assert current_campaign_id == "rotrl"
