import os
from typing import Any, Dict

import pymongo
from bson import DBRef, ObjectId
from pymongo.server_api import ServerApi


class DatabaseClient:
    """
    Client for the backing database.

    Attributes:
        mongo_password: Password for the MongoDB user.
        mongo_user: Username for the MongoDB user.
        mongo_host: Hostname for the MongoDB instance.
        mongo_scheme: URL scheme for the MongoDB connection.
    """

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
            return DatabaseClient(os.getenv("MONGO_PASSWORD"))
        return DatabaseClient.instance

    def get_current_game_context(self) -> Dict[str, Any]:
        """
        Gets the game context from the database.

        return: Dict containing the game context data.
        """
        current_game_context_id: DBRef = self.get_context_tracker()["active_context"]
        game_context = self.db.game_context.find_one(
            {"_id": current_game_context_id.id}
        )
        if game_context is None:
            raise Exception("No current game context found.")
        return game_context

    def get_context_by_campaign_name(self, campaign_name: str):
        """
        Gets the game context from the database, using the campaign name.

        param campaign_name: Name of the campaign to retrieve.
        return: Dict containing the game context data.
        """
        game_contexts = list(self.db.game_context.find({"name": campaign_name}))
        if len(game_contexts) == 0:
            raise Exception(
                "No campaign found with that name. Make sure case is correct"
            )
        elif len(game_contexts) > 1:
            raise Exception("Multiple game_contexts found with that name.")
        return game_contexts[0]

    def get_game_master(self) -> str:
        """
        Gets the game master for the current game context.

        return: String containing the game master's user ID.
        """
        game_context = self.get_current_game_context()
        return game_context["game_master"]

    def get_context_tracker(self):
        """
        Gets the entity that tracks the current game context from the database.

        return: Dict containing the game context data.
        """
        context_tracker = self.db.current_game_context.find_one(
            {"tracking_context": True}
        )
        if context_tracker is None:
            raise Exception("Could not locate context tracking entity.")

        return context_tracker

    def update_game_context(self, game_context: Dict[str, Any]) -> None:
        """
        Updates the game context in the database.

        param game_context: Dict containing the game context data.
        """
        update_filter = {"_id": game_context["_id"]}
        self.db.game_context.update_one(update_filter, {"$set": game_context})

    def update_active_game_context(self, id_ref: ObjectId) -> None:
        """
        Updates the active game context in the database.

        param id_ref: DBRef containing the game context ID.
        """
        context_tracker = self.get_context_tracker()
        self.db.current_game_context.update_one(
            {"_id": context_tracker["_id"]},
            {
                "$set": {
                    "active_context": DBRef("game_context", id_ref, "symone_knowledge")
                }
            },
        )
