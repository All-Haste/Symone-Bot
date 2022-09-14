def test_get_current_campaign_id(database_client):
    current_campaign_id = database_client.get_context_tracker()

    assert current_campaign_id is not None
