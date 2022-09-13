from typing import Any, Dict

from google.cloud import datastore
from google.cloud.datastore import Key

DATA_KEY_CAMPAIGN = "campaign"
DATA_KEY_CURRENT_CAMPAIGN = "current_campaign"


class DatabaseClient:
    def __init__(self, project_id: str):
        if project_id is None:
            raise AttributeError("'project_id' cannot be type 'NoneType'")
        self.project_id = project_id
        self.client = datastore.Client(self.project_id)

    def get_current_campaign(self) -> Dict[str, Any]:
        """
        Gets the campaign from GCP Datastore.

        return: Dict containing the campaign data.
        """
        current_campaign_id = self.get_current_campaign_entity()["campaign_id"]
        campaign = self.client.get(
            Key(DATA_KEY_CAMPAIGN, current_campaign_id, project=self.project_id)
        )
        return campaign

    def get_campaign_by_name(self, campaign_name: str):
        """
        Gets the campaign from GCP Datastore.

        param campaign_name: Name of the campaign to retrieve.
        return: Dict containing the campaign data.
        """
        query = self.client.query(kind=DATA_KEY_CAMPAIGN)
        query.add_filter("name", "=", campaign_name)
        campaigns = list(query.fetch())
        if len(campaigns) == 0:
            raise Exception(
                "No campaign found with that name. Make sure case is correct"
            )
        elif len(campaigns) > 1:
            raise Exception("Multiple campaigns found with that name.")
        return campaigns[0]

    def get_game_master(self) -> str:
        """
        Gets the game master for the current campaign.

        return: String containing the game master's user ID.
        """
        campaign = self.get_current_campaign()
        return campaign["game_master"]

    def get_current_campaign_entity(self) -> Dict[str, Any]:
        """
        Gets the entity that tracks the current campaign from GCP Datastore.

        return: Dict containing the campaign data.
        """
        try:
            current_campaign = list(
                self.client.query(kind=DATA_KEY_CURRENT_CAMPAIGN).fetch()
            )[0]
        except IndexError:
            raise Exception("No current campaign set.")

        return current_campaign

    def put_record(self, campaign: Dict[str, Any]) -> None:
        """
        Updates the campaign in GCP Datastore.

        param campaign: Dict containing the campaign data.
        """
        self.client.put(campaign)


# def create_client(project_id: str):
#     """
#     Creates a datastore client.
#
#     param project_id: Project ID to use for the datastore client.
#     """
#     return datastore.Client(project_id)
#
#
# def get_campaign(datastore_client=None) -> Dict[str, Any]:
#     """
#     Gets the campaign from GCP Datastore.
#
#     param datastore_client: Optional datastore client to use, will create if none provided.
#     return: Dict containing the campaign data.
#     """
#     if not datastore_client:
#         datastore_client = create_client(PROJECT_ID)
#     current_campaign_id = get_current_campaign_id_entity(datastore_client)[
#         "campaign_id"
#     ]
#     campaign = datastore_client.get(
#         Key(DATA_KEY_CAMPAIGN, current_campaign_id, project=PROJECT_ID)
#     )
#     return campaign
#
#
# def get_game_master(datastore_client=None) -> str:
#     """
#     Gets the game master for the current campaign.
#
#     param datastore_client: Optional datastore client to use.
#     return: String containing the game master's user ID.
#     """
#     campaign = get_campaign(datastore_client)
#     return campaign["game_master"]
#
#
# def get_current_campaign_id_entity(
#     datastore_client=None, project_id=PROJECT_ID
# ) -> Dict[str, Any]:
#     """
#     Gets the ID for the current campaign from GCP Datastore.
#
#     param datastore_client: Optional datastore client to use, will create if none provided.
#     return: Dict containing the campaign data.
#     """
#     if not datastore_client:
#         datastore_client = create_client(project_id)
#     try:
#         current_campaign = list(
#             datastore_client.query(kind=DATA_KEY_CURRENT_CAMPAIGN).fetch()
#         )[0]
#     except IndexError:
#         raise Exception("No current campaign set.")
#
#     return current_campaign
