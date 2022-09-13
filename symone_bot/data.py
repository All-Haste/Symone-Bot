from typing import Any, Dict

import pymongo
from pymongo.server_api import ServerApi

DATA_KEY_CAMPAIGN = "campaign"
DATA_KEY_CURRENT_CAMPAIGN = "current_campaign"


class DatabaseClient:
    def __init__(
        self,
        mongo_password: str,
        mongo_user: str = "symone-client",
        mongo_host: str = "gamenightserverlessinst.7ncjp.mongodb.net",
        mongo_scheme: str = "mongodb+srv",
    ):
        if mongo_password is None:
            raise AttributeError("'mongo_password' cannot be type 'NoneType'")
        self.client = pymongo.MongoClient(
            f"{mongo_scheme}://{mongo_user}:{mongo_password}@{mongo_host}/?retryWrites=true&w=majority",
            server_api=ServerApi("1"),
        )
        self.db = self.client.symone_knowledge

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(DatabaseClient, cls).__new__(cls)
        return cls.instance

    @staticmethod
    def get_client():
        if not hasattr(DatabaseClient, "instance"):
            raise Exception("DatabaseClient not initialized.")
        return DatabaseClient.instance

    def get_current_campaign(self) -> Dict[str, Any]:
        """
        Gets the campaign from GCP Datastore.

        return: Dict containing the campaign data.
        """
        current_campaign_id = self.get_current_context_id()["active_context"]
        campaign = self.db.game_context.find_one({"_id": current_campaign_id})
        if campaign is None:
            raise Exception("No current campaign found.")
        return campaign

    def get_context_by_campaign_name(self, campaign_name: str):
        """
        Gets the campaign from GCP Datastore.

        param campaign_name: Name of the campaign to retrieve.
        return: Dict containing the campaign data.
        """
        campaigns = self.db.game_context.find({"name": campaign_name})
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

    def get_current_context_id(self) -> Dict[str, Any]:
        """
        Gets the entity that tracks the current campaign from GCP Datastore.

        return: Dict containing the campaign data.
        """
        current_campaign = self.db.current_game_context.find_one(
            {"tracking_context": True}
        )
        if current_campaign is None:
            raise Exception("No current campaign found.")

        return current_campaign

    def update_game_context(self, game_context: Dict[str, Any]) -> None:
        """
        Updates the game context in the database.

        param campaign: Dict containing the campaign data.
        """
        update_filter = {"_id": game_context["_id"]}
        self.db.game_context.update_one(update_filter, {"$set": game_context})
