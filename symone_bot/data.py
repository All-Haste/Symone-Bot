import os
from typing import Any, Dict

from google.cloud import datastore
from google.cloud.datastore import Key

DATA_KEY_CAMPAIGN = "campaign"
DATA_KEY_CURRENT_CAMPAIGN = "current_campaign"

PROJECT_ID = os.getenv("PROJECT_ID")
CURRENT_CAMPAIGN_ENTITY_ID = str(os.getenv("CURRENT_CAMPAIGN_ENTITY_ID"))


def create_client(project_id: str):
    """
    Creates a datastore client.

    param project_id: Project ID to use for the datastore client.
    """
    return datastore.Client(project_id)


def get_campaign(datastore_client=None) -> Dict[str, Any]:
    """
    Gets the campaign from GCP Datastore.

    param datastore_client: Optional datastore client to use, will create if none provided.
    return: Dict containing the campaign data.
    """
    if not datastore_client:
        datastore_client = create_client(PROJECT_ID)
    current_campaign_id = get_current_campaign(datastore_client)
    campaign = datastore_client.get(
        Key(DATA_KEY_CAMPAIGN, current_campaign_id, project=PROJECT_ID)
    )
    return campaign


def get_current_campaign(datastore_client=None) -> str:
    """
    Gets the ID for the current campaign from GCP Datastore.

    param datastore_client: Optional datastore client to use, will create if none provided.
    return: Dict containing the campaign data.
    """
    if not datastore_client:
        datastore_client = create_client(PROJECT_ID)
    campaign = datastore_client.get(
        Key(DATA_KEY_CURRENT_CAMPAIGN, CURRENT_CAMPAIGN_ENTITY_ID, project=PROJECT_ID)
    )
    return campaign
