import pytest

from symone_bot.data import create_client, get_current_campaign_id


def test_create_client(mocker):
    datastore_mock = mocker.patch("symone_bot.data.datastore", autospec=True)
    create_client("foo")

    datastore_mock.Client.assert_called_once_with("foo")


@pytest.mark.skip(reason="This test needs the datastore emulator running")
def test_get_current_campaign_id():
    current_campaign_id = get_current_campaign_id()

    assert current_campaign_id == "rotrl"
