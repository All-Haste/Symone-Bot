def test_get_current_campaign_id(database_client):
    current_campaign_id = database_client.get_current_context_id()

    assert current_campaign_id is not None
