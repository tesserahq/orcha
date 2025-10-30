from pydantic import BaseModel


class NodeKind(BaseModel):
    """Schema representing an available node kind.

    Mirrors the structure defined in app.constants.node_kinds.
    """

    id: str
    name: str
    description: str
    category: str
