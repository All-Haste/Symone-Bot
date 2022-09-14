import pytest

from symone_bot.handler_source import HandlerSource


@pytest.mark.parametrize(
    "handler_source,num",
    [
        (HandlerSource.ASPECT_QUERY, 1),
        (HandlerSource.HELP, 2),
    ],
)
def test__handler_source_values(handler_source, num):
    assert handler_source.value == num
