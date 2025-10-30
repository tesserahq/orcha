# Workflow Node Schema Documentation

This repository defines a schema for workflow nodes inspired by declarative-style nodes from n8n.

---

## Schema Overview

### 1. Node Description
Defines the node’s metadata and interface.

| Field            | Description                                              |
|------------------|----------------------------------------------------------|
| `displayName`    | Human-readable name of the node.                         |
| `name`           | Internal identifier for the node.                        |
| `version`        | Version number of the node.                              |
| `description`    | Short summary of the node’s purpose.                     |
| `inputs`         | Array of input channel identifiers (e.g., `["main"]`).   |
| `outputs`        | Array of output channel identifiers.                      |
| `credentials`    | *(Optional)* Credentials required by the node.           |
| `requestDefaults`| *(Optional)* Default HTTP settings for operations.       |
| `properties`     | Array of fields defining UI and operations available.    |

---

### 2. Properties
Defines UI fields and available operations.

Each property field may include:
- `displayName`: Label shown to the user.
- `name`: Internal field name.
- `type`: Data type (e.g., `string`, `options`, `boolean`).
- `default`: Default value.
- `required`: Whether the field is mandatory.
- `description`: Explanation of the field.
- `options`: *(for `type = "options"`)* Array of `OptionItem`.
- `displayOptions`: Conditions controlling visibility.
- `routing`: *(Optional)* HTTP request definition when the field/option is selected.

---

### 3. Routing
Defines how the node interacts with external APIs based on user input.

```json
{
  "routing": {
    "request": {
      "method": "GET",
      "url": "/api/endpoint",
      "qs": {
        "param": "={{$parameter.fieldName}}"
      },
      "body": {...},
      "headers": {...}
    }
  }
}
```

* method: HTTP method (GET, POST, PUT, DELETE, …).
* url: Endpoint path (may contain dynamic expressions).
* qs: Query‐string parameters to add to URL.
* body: Payload for methods like POST/PUT.
* headers: Custom HTTP headers.


### 4. Example Schema in Python (using @dataclass)

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class RequestConfig:
    method: str
    url: str
    headers: Optional[Dict[str, Any]] = None
    qs: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None

@dataclass
class Routing:
    request: RequestConfig

@dataclass
class OptionItem:
    name: str
    value: Any
    description: Optional[str] = None
    action: Optional[str] = None
    routing: Optional[Routing] = None
    displayOptions: Optional[Dict[str, Any]] = None

@dataclass
class PropertyField:
    displayName: str
    name: str
    type: str
    default: Any = None
    required: bool = False
    description: Optional[str] = None
    options: Optional[List[OptionItem]] = None
    displayOptions: Optional[Dict[str, Any]] = None
    routing: Optional[Routing] = None

@dataclass
class NodeDescription:
    displayName: str
    name: str
    version: Any
    description: str
    inputs: List[str]
    outputs: List[str]
    credentials: Optional[List[Dict[str, Any]]] = None
    requestDefaults: Optional[RequestConfig] = None
    properties: List[PropertyField] = field(default_factory=list)

@dataclass
class NodeSchema:
    description: NodeDescription
```
