from symone_bot.aspects import Aspect


def test_aspect_help():
    test_aspect = Aspect("foo", "a foo aspect")
    actual = test_aspect.help()

    assert actual == "`foo`: a foo aspect."
