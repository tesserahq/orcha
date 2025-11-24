"""Node category constants.

Category keys are stable identifiers suitable for storage and lookups.
Expose them as constants to avoid string literals throughout the codebase.
"""

from typing import Literal

# Category constants
CATEGORY_TRIGGER = "trigger"
CATEGORY_CORE = "core"
CATEGORY_FLOW = "flow"
CATEGORY_DATA_TRANSFORMATION = "data_transformation"
CATEGORY_ACTION_APP = "action_app"

# Type alias for category keys
CategoryKey = Literal["trigger", "core", "flow", "data_transformation", "action_app"]

__all__ = [
    "CATEGORY_TRIGGER",
    "CATEGORY_CORE",
    "CATEGORY_FLOW",
    "CATEGORY_DATA_TRANSFORMATION",
    "CATEGORY_ACTION_APP",
    "CategoryKey",
]
