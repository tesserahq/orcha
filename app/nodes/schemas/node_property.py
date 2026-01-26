"""Node property schemas for defining node properties and their configurations.

This module provides Pydantic models for defining node properties with type-specific
options and configurations. It supports all property types including string, number,
boolean, options, collections, and more.
"""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel

# Property Type Definitions
NodePropertyType = Literal[
    "boolean",
    "collection",
    "color",
    "dateTime",
    "hidden",
    "json",
    "notice",
    "multiOptions",
    "number",
    "options",
    "string",
    "filter",
    "button",
    "callout",
    "credentialsSelect",
    "resourceLocator",
    "resourceMapper",
    "assignmentCollection",
    "credentials",
    "workflowSelector",
    "curlImport",
    "fixedCollection",
]

# SQL Dialect Types
SQLDialect = Literal[
    "StandardSQL",
    "PostgreSQL",
    "MySQL",
    "OracleDB",
    "MariaSQL",
    "MSSQL",
    "SQLite",
    "Cassandra",
    "PLSQL",
]

# Code Autocomplete Types
CodeAutocompleteType = Literal["function", "functionItem"]

# Editor Types
EditorType = Literal[
    "codeNodeEditor",
    "jsEditor",
    "htmlEditor",
    "sqlEditor",
    "cssEditor",
]

# Resource Mapper Mode Types
ResourceMapperMode = Literal["add", "update", "upsert", "map"]

# Filter Version Types
FilterVersion = Union[Literal[1, 2], Dict[str, Any]]

# Type Validation Types
TypeValidation = Union[Literal["strict", "loose"], Dict[str, Any]]

# Field Type (for assignments)
FieldType = Literal[
    "string",
    "number",
    "boolean",
    "dateTime",
    "json",
    "array",
    "object",
]


# Supporting Models
class DisplayOptions(BaseModel):
    """Conditional visibility options for properties."""

    show: Optional[Dict[str, List[Any]]] = None
    """Show property when these conditions are met."""

    hide: Optional[Dict[str, List[Any]]] = None
    """Hide property when these conditions are met."""


class MultipleValuesOptions(BaseModel):
    """Options for properties that support multiple values."""

    multiple_values: bool = False
    """Enable multiple values for this property."""

    multiple_value_button_text: Optional[str] = None
    """Custom text for the 'Add Another' button."""

    sortable: Optional[bool] = None
    """Allow reordering when multiple_values is enabled."""


class NodePropertyOption(BaseModel):
    """Option for options/multiOptions property types."""

    name: str
    """Display name of the option."""

    value: Any
    """Value of the option."""

    description: Optional[str] = None
    """Optional description for the option."""


class NodePropertyCollectionValue(BaseModel):
    """A single value within a collection."""

    display_name: str
    """Label shown in UI."""

    name: str
    """Internal property name (camelCase)."""

    type: NodePropertyType
    """One of the available property types."""

    default: Any = None
    """Default value."""

    description: Optional[str] = None
    """Help text."""

    placeholder: Optional[str] = None
    """Placeholder text."""

    required: Optional[bool] = None
    """Whether the property is required."""


class NodePropertyCollection(BaseModel):
    """Collection of properties grouped together."""

    display_name: str
    """Label shown in UI."""

    name: str
    """Internal collection name (camelCase)."""

    values: List[NodePropertyCollectionValue]
    """List of properties in this collection."""


# Type-Specific Options
class NoticeTypeOptions(BaseModel):
    """Type options for 'notice' property type."""

    container_class: Optional[str] = None
    """CSS class for styling the notice container."""


class StringTypeOptions(BaseModel):
    """Type options for 'string' property type."""

    password: Optional[bool] = None
    """Render as password field."""

    rows: Optional[int] = None
    """Number of rows for multi-line text."""

    code_autocomplete: Optional[CodeAutocompleteType] = None
    """Enable code autocomplete."""

    editor: Optional[EditorType] = None
    """Use code editor instead of plain text field."""

    editor_is_read_only: Optional[bool] = None
    """Make editor read-only."""

    sql_dialect: Optional[SQLDialect] = None
    """SQL dialect for sqlEditor."""

    multiple_values: Optional[bool] = None
    """Allow multiple string values."""

    multiple_value_button_text: Optional[str] = None
    """Custom text for 'Add Another' button."""

    sortable: Optional[bool] = None
    """Allow reordering when multiple_values is enabled."""


class NumberTypeOptions(BaseModel):
    """Type options for 'number' property type."""

    min_value: Optional[float] = None
    """Minimum allowed value."""

    max_value: Optional[float] = None
    """Maximum allowed value."""

    number_precision: Optional[int] = None
    """Number of decimal places."""

    multiple_values: Optional[bool] = None
    """Allow multiple number values."""

    multiple_value_button_text: Optional[str] = None
    """Custom text for 'Add Another' button."""

    sortable: Optional[bool] = None
    """Allow reordering when multiple_values is enabled."""


class BooleanTypeOptions(BaseModel):
    """Type options for 'boolean' property type."""

    multiple_values: Optional[bool] = None
    """Allow multiple boolean values."""

    multiple_value_button_text: Optional[str] = None
    """Custom text for 'Add Another' button."""

    sortable: Optional[bool] = None
    """Allow reordering when multiple_values is enabled."""


class OptionsTypeOptions(BaseModel):
    """Type options for 'options' property type."""

    load_options_method: Optional[str] = None
    """Method name to dynamically load options."""

    load_options_depends_on: Optional[List[str]] = None
    """Properties that trigger option reload."""

    load_options: Optional[Dict[str, Any]] = None
    """Additional configuration for loading options."""

    allow_arbitrary_values: Optional[bool] = None
    """Allow values not in the options list."""

    multiple_values: Optional[bool] = None
    """Allow multiple option values."""

    multiple_value_button_text: Optional[str] = None
    """Custom text for 'Add Another' button."""

    sortable: Optional[bool] = None
    """Allow reordering when multiple_values is enabled."""


class MultiOptionsTypeOptions(OptionsTypeOptions):
    """Type options for 'multiOptions' property type.

    Inherits all options from OptionsTypeOptions.
    """

    pass


class FixedCollectionTypeOptions(BaseModel):
    """Type options for 'fixedCollection' property type."""

    multiple_values: Optional[bool] = None
    """Allow multiple collection entries."""

    sortable: Optional[bool] = None
    """Allow reordering when multiple_values is enabled."""

    min_required_fields: Optional[int] = None
    """Minimum number of entries required."""

    max_allowed_fields: Optional[int] = None
    """Maximum number of entries allowed."""


class JsonTypeOptions(BaseModel):
    """Type options for 'json' property type."""

    always_open_edit_window: Optional[bool] = None
    """Always open in editor window."""

    multiple_values: Optional[bool] = None
    """Allow multiple JSON values."""

    multiple_value_button_text: Optional[str] = None
    """Custom text for 'Add Another' button."""

    sortable: Optional[bool] = None
    """Allow reordering when multiple_values is enabled."""


class NodePropertyAction(BaseModel):
    """Action configuration for button properties."""

    type: Literal["askAiCodeGeneration"]
    """Type of action."""

    handler: Optional[str] = None
    """Handler function name."""

    target: Optional[str] = None
    """Target identifier."""


class ButtonConfig(BaseModel):
    """Button configuration for button properties."""

    action: Union[str, NodePropertyAction]
    """Action identifier or action object."""

    label: Optional[str] = None
    """Custom button label."""

    has_input_field: Optional[bool] = None
    """Whether the button has an input field."""

    input_field_max_length: Optional[int] = None
    """Maximum length for input field."""


class ButtonTypeOptions(BaseModel):
    """Type options for 'button' property type."""

    button_config: Optional[ButtonConfig] = None
    """Button configuration."""


class ColorTypeOptions(BaseModel):
    """Type options for 'color' property type."""

    show_alpha: Optional[bool] = None
    """Show alpha/opacity channel."""

    multiple_values: Optional[bool] = None
    """Allow multiple color values."""

    multiple_value_button_text: Optional[str] = None
    """Custom text for 'Add Another' button."""

    sortable: Optional[bool] = None
    """Allow reordering when multiple_values is enabled."""


class HiddenTypeOptions(BaseModel):
    """Type options for 'hidden' property type."""

    expirable: Optional[bool] = None
    """Mark value as expirable (for credentials)."""


class CalloutAction(BaseModel):
    """Action configuration for callout properties."""

    type: str
    """Type of callout action."""

    label: str
    """Label text for the action button."""

    icon: Optional[str] = None
    """Icon identifier."""

    template_id: Optional[str] = None
    """Template ID (for 'openSampleWorkflowTemplate' type)."""


class CalloutTypeOptions(BaseModel):
    """Type options for 'callout' property type."""

    callout_action: Optional[CalloutAction] = None
    """Action to perform when clicked."""


class ResourceMapperTypeOptions(BaseModel):
    """Type options for 'resourceMapper' property type."""

    resource_mapper: Optional[Dict[str, Any]] = None
    """Configuration for resource mapping."""


class FilterTypeOptions(BaseModel):
    """Type options for 'filter' property type."""

    filter: Optional[Dict[str, Any]] = None
    """Filter configuration."""


class AssignmentTypeOptions(BaseModel):
    """Type options for 'assignmentCollection' property type."""

    assignment: Optional[Dict[str, Any]] = None
    """Assignment configuration."""


# Union type for all type options
NodePropertyTypeOptions = Union[
    NoticeTypeOptions,
    StringTypeOptions,
    NumberTypeOptions,
    BooleanTypeOptions,
    OptionsTypeOptions,
    MultiOptionsTypeOptions,
    FixedCollectionTypeOptions,
    JsonTypeOptions,
    ButtonTypeOptions,
    ColorTypeOptions,
    HiddenTypeOptions,
    CalloutTypeOptions,
    ResourceMapperTypeOptions,
    FilterTypeOptions,
    AssignmentTypeOptions,
    MultipleValuesOptions,
]


# Main Property Model
class NodeProperty(BaseModel):
    """Main property model for defining node properties.

    Every property follows this structure with type-specific options available
    through the type_options field.
    """

    display_name: str
    """Label shown in UI."""

    name: str
    """Internal property name (camelCase)."""

    type: NodePropertyType
    """One of the available property types."""

    type_options: Optional[NodePropertyTypeOptions] = None
    """Type-specific options."""

    default: Any = None
    """Default value."""

    description: Optional[str] = None
    """Help text."""

    hint: Optional[str] = None
    """Additional hint text."""

    display_options: Optional[DisplayOptions] = None
    """Conditional visibility options."""

    disabled_options: Optional[DisplayOptions] = None
    """Options for disabling the property."""

    options: Optional[
        List[Union[NodePropertyOption, "NodeProperty", NodePropertyCollection]]
    ] = None
    """Options for the property (for options, multiOptions, fixedCollection types)."""

    placeholder: Optional[str] = None
    """Placeholder text."""

    required: Optional[bool] = None
    """Whether the property is required."""

    credential_types: Optional[List[str]] = None
    """Credential types (for credentialsSelect and credentials types)."""


# Example Properties Class
# class ExampleProperties:
#     """Static methods that return example property instances for each type."""

#     @staticmethod
#     def notice_property() -> NodeProperty:
#         """Get an example notice property."""
#         return NodeProperty(
#             display_name="Info message",
#             name="notice",
#             type="notice",
#             default="",
#             description="This is an informational notice",
#         )

#     @staticmethod
#     def string_property() -> NodeProperty:
#         """Get an example string property."""
#         return NodeProperty(
#             display_name="Name",
#             name="name",
#             type="string",
#             default="",
#             placeholder="Enter name",
#             description="The name of the item",
#         )

#     @staticmethod
#     def number_property() -> NodeProperty:
#         """Get an example number property."""
#         return NodeProperty(
#             display_name="Count",
#             name="count",
#             type="number",
#             default=0,
#             description="Number of items",
#         )

#     @staticmethod
#     def boolean_property() -> NodeProperty:
#         """Get an example boolean property."""
#         return NodeProperty(
#             display_name="Enabled",
#             name="enabled",
#             type="boolean",
#             default=False,
#             description="Whether the feature is enabled",
#         )

#     @staticmethod
#     def options_property() -> NodeProperty:
#         """Get an example options property."""
#         return NodeProperty(
#             display_name="Operation",
#             name="operation",
#             type="options",
#             options=[
#                 NodePropertyOption(name="Create", value="create"),
#                 NodePropertyOption(name="Update", value="update"),
#                 NodePropertyOption(name="Delete", value="delete"),
#             ],
#             default="create",
#             description="The operation to perform",
#         )

#     @staticmethod
#     def multi_options_property() -> NodeProperty:
#         """Get an example multiOptions property."""
#         return NodeProperty(
#             display_name="Fields",
#             name="fields",
#             type="multiOptions",
#             options=[
#                 NodePropertyOption(name="Name", value="name"),
#                 NodePropertyOption(name="Email", value="email"),
#                 NodePropertyOption(name="Phone", value="phone"),
#             ],
#             default=[],
#             description="Select fields to include",
#         )

#     @staticmethod
#     def fixed_collection_property() -> NodeProperty:
#         """Get an example fixedCollection property."""
#         return NodeProperty(
#             display_name="Address",
#             name="address",
#             type="fixedCollection",
#             type_options=FixedCollectionTypeOptions(
#                 multiple_values=True,
#                 sortable=True,
#             ),
#             default={},
#             placeholder="Add Address",
#             options=[
#                 NodePropertyCollection(
#                     display_name="Address Fields",
#                     name="addressFields",
#                     values=[
#                         NodePropertyCollectionValue(
#                             display_name="Street",
#                             name="street",
#                             type="string",
#                             default="",
#                         ),
#                         NodePropertyCollectionValue(
#                             display_name="City",
#                             name="city",
#                             type="string",
#                             default="",
#                         ),
#                     ],
#                 )
#             ],
#         )

#     @staticmethod
#     def json_property() -> NodeProperty:
#         """Get an example json property."""
#         return NodeProperty(
#             display_name="JSON Data",
#             name="jsonData",
#             type="json",
#             type_options=JsonTypeOptions(always_open_edit_window=True),
#             default={},
#             description="JSON data object",
#         )

#     @staticmethod
#     def date_time_property() -> NodeProperty:
#         """Get an example dateTime property."""
#         return NodeProperty(
#             display_name="Date",
#             name="date",
#             type="dateTime",
#             default="",
#             description="Select a date and time",
#         )

#     @staticmethod
#     def color_property() -> NodeProperty:
#         """Get an example color property."""
#         return NodeProperty(
#             display_name="Color",
#             name="color",
#             type="color",
#             default="#000000",
#         )

#     @staticmethod
#     def hidden_property() -> NodeProperty:
#         """Get an example hidden property."""
#         return NodeProperty(
#             display_name="Hidden Field",
#             name="hiddenValue",
#             type="hidden",
#             default="computed-value",
#         )

#     @staticmethod
#     def collection_property() -> NodeProperty:
#         """Get an example collection property."""
#         return NodeProperty(
#             display_name="Additional Fields",
#             name="additionalFields",
#             type="collection",
#             placeholder="Add Field",
#             default={},
#         )
