import pytest

from symone_bot.metadata import QueryMetaData


def test_metadata_raises_attribute_error_when_no_user_id():
    with pytest.raises(AttributeError):
        QueryMetaData(None)


def test_metadata_has_user_id():
    metadata = QueryMetaData("foo")

    assert metadata.user_id == "foo"
