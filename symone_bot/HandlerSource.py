from enum import Enum


class HandlerSource(Enum):
    """Enum for different types of Slack event handlers"""

    ASPECT_QUERY = 1
    HELP = 2
