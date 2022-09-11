import os
from typing import Any, Dict

from google.cloud import datastore
from google.cloud.datastore import Key

DATA_KEY_CAMPAIGN = "campaign"
DATA_KEY_CURRENT_CAMPAIGN = "current_campaign"
PROJECT_ID = os.getenv("PROJECT_ID")


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
    current_campaign_id = get_current_campaign_id_entity(datastore_client)[
        "campaign_id"
    ]
    campaign = datastore_client.get(
        Key(DATA_KEY_CAMPAIGN, current_campaign_id, project=PROJECT_ID)
    )
    return campaign


def get_current_campaign_id_entity(
    datastore_client=None, project_id=PROJECT_ID
) -> Dict[str, Any]:
    """
    Gets the ID for the current campaign from GCP Datastore.

    param datastore_client: Optional datastore client to use, will create if none provided.
    return: Dict containing the campaign data.
    """
    if not datastore_client:
        datastore_client = create_client(project_id)
    try:
        current_campaign = list(
            datastore_client.query(kind=DATA_KEY_CURRENT_CAMPAIGN).fetch()
        )[0]
    except IndexError:
        raise Exception("No current campaign set.")

    return current_campaign
