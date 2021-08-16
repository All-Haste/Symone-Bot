from symone_bot.commands import create_client


def test_create_client(mocker):
    datastore_mock = mocker.patch("symone_bot.commands.datastore", autospec=True)

    create_client("foo")

    datastore_mock.Client.assert_called_once_with("foo")
