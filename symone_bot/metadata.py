class QueryMetaData:
    """Stores metadata about the incoming query such as user-id, headers, etc."""

    def __init__(self, user_id: str):
        if not isinstance(user_id, str):
            raise AttributeError("'user_id' cannot be None.")
        self.user_id = user_id
