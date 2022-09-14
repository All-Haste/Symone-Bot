from symone_bot.aspects import Aspect, aspect_dict


def test_aspect_help():
    test_aspect = Aspect("foo", "a foo aspect", "foo")
    actual = test_aspect.help()

    assert actual == "`foo`: a foo aspect."


def test_campaign_aspect_is_singleton():
    campaign_aspect = aspect_dict.get("campaign")
    assert campaign_aspect.is_singleton
