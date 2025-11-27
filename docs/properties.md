# Node Property Types

This document describes all available property types in nodes and how to use them with Python/Pydantic schemas.

## Property Type Definitions

All property types are defined in `app/schemas/node_property.py`:

```python
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
]
```

## Property Structure

Every property follows the `NodeProperty` Pydantic model:

```python
class NodeProperty(BaseModel):
    display_name: str = Field(..., alias="display_name")
    """Label shown in UI."""

    name: str
    """Internal property name (camelCase)."""

    type: NodePropertyType
    """One of the available property types."""

    type_options: Optional[NodePropertyTypeOptions] = Field(None, alias="typeOptions")
    """Type-specific options."""

    default: Any = None
    """Default value."""

    description: Optional[str] = None
    """Help text."""

    hint: Optional[str] = None
    """Additional hint text."""

    display_options: Optional[DisplayOptions] = Field(None, alias="display_options")
    """Conditional visibility options."""

    disabled_options: Optional[DisplayOptions] = Field(None, alias="disabledOptions")
    """Options for disabling the property."""

    options: Optional[List[Union[NodePropertyOption, NodeProperty, NodePropertyCollection]]] = None
    """Options for the property (for options, multiOptions, fixedCollection types)."""

    placeholder: Optional[str] = None
    """Placeholder text."""

    required: Optional[bool] = None
    """Whether the property is required."""

```

## Property Type Options

The `type_options` field provides type-specific configuration options that customize how a property behaves and appears in the UI. Different options apply to different property types, and some options are universal (available for all property types).

### Overview

Type options are passed via the `type_options` parameter when creating a `NodeProperty`. Each property type has its own set of supported options, though some options like `multipleValues` are universal and work with all property types.

### Universal Options

These options can be used with any property type:

#### `multipleValues` and `multipleValueButtonText`
Allows a property to accept multiple values. When enabled, users can add multiple entries for the property.

- **`multipleValues`**: `bool` - Set to `true` to enable multiple values
- **`multipleValueButtonText`**: `str` - Custom text for the "Add Another" button (defaults to "Add Value" if not specified)

**Supported by**: All property types

#### `sortable`
When `multipleValues` is enabled, this allows users to reorder the multiple values via drag-and-drop.

- **`sortable`**: `bool` - Set to `true` to enable reordering

**Supported by**: All property types (when `multipleValues: true`)

### String Type Options

Options specific to `type: 'string'`:

#### `password`
Renders the input field as a password field (text is masked).

- **`password`**: `bool` - Set to `true` to mask input

#### `rows`
Creates a multi-line text area instead of a single-line input.

- **`rows`**: `int` - Number of visible rows in the text area

#### `codeAutocomplete`
Enables code autocomplete features in the editor.

- **`codeAutocomplete`**: `'function' | 'functionItem'` - Type of autocomplete to enable

#### `editor`
Uses a code editor instead of a plain text field.

- **`editor`**: `'codeNodeEditor' | 'jsEditor' | 'htmlEditor' | 'sqlEditor' | 'cssEditor'` - Type of code editor to use

#### `editorIsReadOnly`
Makes the code editor read-only (users cannot edit).

- **`editorIsReadOnly`**: `bool` - Set to `true` to make editor read-only

#### `sqlDialect`
When `editor: 'sqlEditor'` is set, specifies the SQL dialect for syntax highlighting and validation.

- **`sqlDialect`**: `'StandardSQL' | 'PostgreSQL' | 'MySQL' | 'OracleDB' | 'MariaSQL' | 'MSSQL' | 'SQLite' | 'Cassandra' | 'PLSQL'` - SQL dialect to use

### Number Type Options

Options specific to `type: 'number'`:

#### `minValue` and `maxValue`
Constrains the numeric input to a specific range.

- **`minValue`**: `float` - Minimum allowed value
- **`maxValue`**: `float` - Maximum allowed value

#### `numberPrecision`
Controls the number of decimal places allowed.

- **`numberPrecision`**: `int` - Number of decimal places (0 for integers)

### Options/MultiOptions Type Options

Options specific to `type: 'options'` and `type: 'multiOptions'`:

#### `loadOptionsMethod`
Dynamically loads options from a method in the node class. The method should return an array of option objects.

- **`loadOptionsMethod`**: `str` - Name of the method to call for loading options

#### `loadOptionsDependsOn`
List of property names that, when changed, trigger a reload of the options.

- **`loadOptionsDependsOn`**: `List[str]` - Array of property names that trigger reload

#### `loadOptions`
Additional configuration for loading options, including routing information.

- **`loadOptions`**: `Dict[str, Any]` - Configuration object with routing, operations, etc.

#### `allowArbitraryValues`
Allows users to enter values that are not in the predefined options list.

- **`allowArbitraryValues`**: `bool` - Set to `true` to allow custom values

### Fixed Collection Type Options

Options specific to `type: 'fixedCollection'`:

#### `minRequiredFields` and `maxAllowedFields`
Constrains the number of collection entries when `multipleValues` is enabled.

- **`minRequiredFields`**: `int` - Minimum number of entries required
- **`maxAllowedFields`**: `int` - Maximum number of entries allowed

### JSON Type Options

Options specific to `type: 'json'`:

#### `alwaysOpenEditWindow`
Forces the JSON editor to always open in a separate editor window, useful for large JSON objects.

- **`alwaysOpenEditWindow`**: `bool` - Set to `true` to always open in editor window

### Button Type Options

Options specific to `type: 'button'`:

#### `buttonConfig`
Configuration object for button behavior and appearance.

- **`action`**: `str | NodePropertyAction` - Action identifier to trigger when button is clicked
- **`label`**: `str` - Custom button label (defaults to `display_name` if not specified)
- **`hasInputField`**: `bool` - Whether the button has an input field
- **`inputFieldMaxLength`**: `int` - Maximum length for input field (only used if `hasInputField: true`)

**NodePropertyAction** structure:
- **`type`**: `'askAiCodeGeneration'` - Type of action
- **`handler`**: `str` (optional) - Handler function name
- **`target`**: `str` (optional) - Target identifier

### Color Type Options

Options specific to `type: 'color'`:

#### `showAlpha`
Shows the alpha/opacity channel in the color picker.

- **`showAlpha`**: `bool` - Set to `true` to show alpha channel

### Hidden Type Options

Options specific to `type: 'hidden'` (primarily used in credentials):

#### `expirable`
Marks the hidden value as expirable (used in credential configurations).

- **`expirable`**: `bool` - Set to `true` to mark value as expirable

### Notice Type Options

Options specific to `type: 'notice'`:

#### `containerClass`
Applies a custom CSS class to the notice container for styling.

- **`containerClass`**: `str` - CSS class name to apply

### Callout Type Options

Options specific to `type: 'callout'`:

#### `calloutAction`
Configuration for the callout button action.

- **`type`**: `str` - Type of callout action (e.g., `'openPreBuiltAgentsCollection'`, `'openSampleWorkflowTemplate'`)
- **`label`**: `str` - Label text for the action button
- **`icon`**: `str` (optional) - Icon identifier
- **`templateId`**: `str` (optional) - Template ID (for `'openSampleWorkflowTemplate'` type)

### Resource Mapper Type Options

Options specific to `type: 'resourceMapper'`:

#### `resourceMapper`
Configuration object for resource field mapping.

- **`mode`**: `'add' | 'update' | 'upsert' | 'map'` - Mapping mode
- **`resourceMapperMethod`**: `str` - Method name to get mapping fields (for local nodes)
- **`localResourceMapperMethod`**: `str` - Method name for external resource mapping
- **`valuesLabel`**: `str` (optional) - Label for the values section
- **`fieldWords`**: `Dict[str, str]` (optional) - Singular and plural forms of "field" for UI text
  - **`singular`**: `str` - Singular form (e.g., "field")
  - **`plural`**: `str` - Plural form (e.g., "fields")
- **`addAllFields`**: `bool` (optional) - Whether to show "Add All Fields" option
- **`noFieldsError`**: `str` (optional) - Error message when no fields are available
- **`multiKeyMatch`**: `bool` (optional) - Whether to allow multi-key matching
- **`supportAutoMap`**: `bool` (optional) - Whether to support automatic field mapping
- **`hideNoDataError`**: `bool` (optional) - Whether to hide "no data" error messages
- **`matchingFieldsLabels`**: `Dict[str, str]` (optional) - Custom labels for matching fields section
- **`showTypeConversionOptions`**: `bool` (optional) - Whether to show type conversion options
- **`allowEmptyValues`**: `bool` (optional) - Whether to allow empty values in mappings

**Note**: Either `resourceMapperMethod` (for local nodes) or `localResourceMapperMethod` (for external resources) must be provided, but not both.

### Filter Type Options

Options specific to `type: 'filter'`:

#### `filter`
Configuration object for the filter/condition builder.

- **`version`**: `1 | 2 | {}` - Filter version (required for versioning)
- **`caseSensitive`**: `bool | str` - Whether comparisons are case-sensitive (default: `true`)
- **`leftValue`**: `str` (optional) - When set, prevents users from editing the left side of conditions
- **`allowedCombinators`**: `List[str]` (optional) - Allowed combinators like `['and', 'or']` (default: `['and', 'or']`)
- **`maxConditions`**: `int` (optional) - Maximum number of conditions allowed (default: `10`)
- **`typeValidation`**: `'strict' | 'loose' | {}` (optional) - Type validation mode (default: `'strict'`)

### Assignment Collection Type Options

Options specific to `type: 'assignmentCollection'`:

#### `assignment`
Configuration object for variable assignments.

- **`hideType`**: `bool` (optional) - Whether to hide the type selector (visible by default)
- **`defaultType`**: `FieldType | 'string'` (optional) - Default type for new assignments
- **`disableType`**: `bool` (optional) - Whether to disable the type selector (enabled by default)

### Usage Guidelines

1. **Type-Specific Options**: Only use options that are supported by the property type. Using unsupported options may be ignored or cause errors.

2. **Universal Options**: Options like `multipleValues` and `sortable` can be combined with any property type.

3. **Combining Options**: You can combine multiple type options together. For example, a string property can have both `editor: 'jsEditor'` and `codeAutocomplete: 'function'`.

4. **Optional Fields**: All type options are optional. Only specify the options you need to customize the property's behavior.

5. **Default Values**: If an option is not specified, the property will use its default behavior. For example, if `multipleValues` is not set, the property will only accept a single value.

### Common Patterns

#### Pattern 1: String with Code Editor
Use `editor` and `codeAutocomplete` together for code input fields that need autocomplete support.

#### Pattern 2: Options with Dynamic Loading
Use `loadOptionsMethod` and `loadOptionsDependsOn` to create dropdowns that update based on other property values.

#### Pattern 3: Multiple Values with Constraints
Use `multipleValues: true` with `minRequiredFields` and `maxAllowedFields` to create collections with size constraints.

#### Pattern 4: Number with Range Validation
Use `minValue` and `maxValue` together to create numeric inputs with validation boundaries.

## Common Property Types with Examples

### 1. `'notice'`
Displays informational text (non-interactive). Used in ManualTrigger node.

```python
from app.schemas.node_property import NodeProperty

NodeProperty(
    display_name="Info message",
    name="notice",
    type="notice",
    default="",
    description="This is an informational notice",
)
```

**Type Options:**
- `container_class?: str` - CSS class for styling

```python
from app.schemas.node_property import NodeProperty, NoticeTypeOptions

NodeProperty(
    display_name="Info message",
    name="notice",
    type="notice",
    default="",
    description="This is an informational notice",
    type_options=NoticeTypeOptions(container_class="custom-class"),
)
```

### 2. `'string'`
Text input field.

```python
from app.schemas.node_property import NodeProperty

NodeProperty(
    display_name="Name",
    name="name",
    type="string",
    default="",
    placeholder="Enter name",
    description="The name of the item",
)
```

**Type Options:**
- `password?: bool` - Render as password field
- `rows?: int` - Number of rows for multi-line text
- `code_autocomplete?: Literal["function", "functionItem"]` - Enable code autocomplete
- `editor?: Literal["codeNodeEditor", "jsEditor", "htmlEditor", "sqlEditor", "cssEditor"]` - Use code editor
- `editor_is_read_only?: bool` - Make editor read-only
- `multiple_values?: bool` - Allow multiple string values

```python
from app.schemas.node_property import NodeProperty, StringTypeOptions

NodeProperty(
    display_name="Password",
    name="password",
    type="string",
    default="",
    type_options=StringTypeOptions(password=True),
)

NodeProperty(
    display_name="Code",
    name="code",
    type="string",
    default="",
    type_options=StringTypeOptions(
        editor="jsEditor",
        editor_is_read_only=False,
        code_autocomplete="function",
    ),
)
```

### 3. `'number'`
Numeric input field.

```python
from app.schemas.node_property import NodeProperty

NodeProperty(
    display_name="Count",
    name="count",
    type="number",
    default=0,
    description="Number of items",
)
```

**Type Options:**
- `min_value?: float` - Minimum allowed value
- `max_value?: float` - Maximum allowed value
- `number_precision?: int` - Decimal precision
- `multiple_values?: bool` - Allow multiple number values

```python
from app.schemas.node_property import NodeProperty, NumberTypeOptions

NodeProperty(
    display_name="Age",
    name="age",
    type="number",
    default=0,
    type_options=NumberTypeOptions(
        min_value=0,
        max_value=120,
        number_precision=0,
    ),
)
```

### 4. `'boolean'`
Checkbox/toggle field.

```python
from app.schemas.node_property import NodeProperty

NodeProperty(
    display_name="Enabled",
    name="enabled",
    type="boolean",
    default=False,
    description="Whether the feature is enabled",
)
```

**Type Options:**
- `multiple_values?: bool` - Allow multiple boolean values

```python
from app.schemas.node_property import NodeProperty, BooleanTypeOptions

NodeProperty(
    display_name="Flags",
    name="flags",
    type="boolean",
    default=False,
    type_options=BooleanTypeOptions(multiple_values=True),
)
```

### 5. `'options'`
Single-select dropdown.

```python
from app.schemas.node_property import NodeProperty, NodePropertyOption

NodeProperty(
    display_name="Operation",
    name="operation",
    type="options",
    options=[
        NodePropertyOption(name="Create", value="create"),
        NodePropertyOption(name="Update", value="update"),
        NodePropertyOption(name="Delete", value="delete"),
    ],
    default="create",
    description="The operation to perform",
)
```

**Type Options:**
- `load_options_method?: str` - Method name to dynamically load options
- `load_options_depends_on?: List[str]` - Properties that trigger option reload
- `allow_arbitrary_values?: bool` - Allow values not in the options list

```python
from app.schemas.node_property import NodeProperty, NodePropertyOption, OptionsTypeOptions

NodeProperty(
    display_name="Category",
    name="category",
    type="options",
    options=[
        NodePropertyOption(name="Category 1", value="cat1"),
        NodePropertyOption(name="Category 2", value="cat2"),
    ],
    default="cat1",
    type_options=OptionsTypeOptions(
        load_options_method="getCategories",
        load_options_depends_on=["resource"],
        allow_arbitrary_values=True,
    ),
)
```

### 6. `'multiOptions'`
Multi-select dropdown (allows multiple selections).

```python
from app.schemas.node_property import NodeProperty, NodePropertyOption

NodeProperty(
    display_name="Fields",
    name="fields",
    type="multiOptions",
    options=[
        NodePropertyOption(name="Name", value="name"),
        NodePropertyOption(name="Email", value="email"),
        NodePropertyOption(name="Phone", value="phone"),
    ],
    default=[],
    description="Select fields to include",
)
```

**Type Options:**
- Same as `'options'` type
- `allow_arbitrary_values?: bool` - Allow values not in the options list

### 7. `'fixedCollection'`
Grouped collection of fields. Can be repeated if `multiple_values` is enabled.

```python
from app.schemas.node_property import (
    NodeProperty,
    NodePropertyCollection,
    NodePropertyCollectionValue,
    FixedCollectionTypeOptions,
)

NodeProperty(
    display_name="Address",
    name="address",
    type="fixedCollection",
    type_options=FixedCollectionTypeOptions(
        multiple_values=True,  # Allow multiple address entries
        sortable=True,  # Allow reordering
    ),
    default={},
    placeholder="Add Address",
    options=[
        NodePropertyCollection(
            display_name="Address Fields",
            name="addressFields",
            values=[
                NodePropertyCollectionValue(
                    display_name="Street",
                    name="street",
                    type="string",
                    default="",
                ),
                NodePropertyCollectionValue(
                    display_name="City",
                    name="city",
                    type="string",
                    default="",
                ),
                NodePropertyCollectionValue(
                    display_name="State",
                    name="state",
                    type="string",
                    default="",
                ),
            ],
        )
    ],
)
```

**Type Options:**
- `multiple_values?: bool` - Allow multiple collection entries
- `sortable?: bool` - Allow reordering when multiple_values is true
- `min_required_fields?: int` - Minimum number of fields required
- `max_allowed_fields?: int` - Maximum number of fields allowed

### 8. `'json'`
JSON editor field.

```python
from app.schemas.node_property import NodeProperty, JsonTypeOptions

NodeProperty(
    display_name="JSON Data",
    name="jsonData",
    type="json",
    type_options=JsonTypeOptions(always_open_edit_window=True),  # Always open in editor window
    default={},
    description="JSON data object",
)
```

**Type Options:**
- `always_open_edit_window?: bool` - Always open in editor window (useful for large JSON)

### 9. `'dateTime'`
Date and time picker.

```python
from app.schemas.node_property import NodeProperty

NodeProperty(
    display_name="Date",
    name="date",
    type="dateTime",
    default="",
    description="Select a date and time",
)
```

### 10. `'button'`
Action button (triggers actions in the UI).

```python
from app.schemas.node_property import NodeProperty, ButtonTypeOptions, ButtonConfig

NodeProperty(
    display_name="Open Chat",
    name="openChat",
    type="button",
    type_options=ButtonTypeOptions(
        button_config=ButtonConfig(
            action="openChat",
            label="Open Chat Window",
            has_input_field=False,
        )
    ),
    default="",
)
```

**Type Options:**
- `button_config?: ButtonConfig` - Button configuration with action, label, has_input_field, and input_field_max_length

### 11. `'color'`
Color picker.

```python
from app.schemas.node_property import NodeProperty

NodeProperty(
    display_name="Color",
    name="color",
    type="color",
    default="#000000",
)
```

**Type Options:**
- `show_alpha?: bool` - Show alpha/opacity channel

```python
from app.schemas.node_property import NodeProperty, ColorTypeOptions

NodeProperty(
    display_name="Color",
    name="color",
    type="color",
    default="#000000",
    type_options=ColorTypeOptions(show_alpha=True),
)
```

### 12. `'hidden'`
Hidden field (not visible in UI, but value is stored).

```python
from app.schemas.node_property import NodeProperty

NodeProperty(
    display_name="Hidden Field",
    name="hiddenValue",
    type="hidden",
    default="computed-value",
)
```

**Type Options:**
- `expirable?: bool` - For credentials only

```python
from app.schemas.node_property import NodeProperty, HiddenTypeOptions

NodeProperty(
    display_name="Hidden Credential",
    name="hiddenCredential",
    type="hidden",
    default="",
    type_options=HiddenTypeOptions(expirable=True),
)
```

### 13. `'collection'`
Dynamic collection of key-value pairs.

```python
from app.schemas.node_property import NodeProperty

NodeProperty(
    display_name="Additional Fields",
    name="additionalFields",
    type="collection",
    placeholder="Add Field",
    default={},
)
```

### 14. `'callout'`
Callout/info box with optional action.

```python
from app.schemas.node_property import NodeProperty, CalloutTypeOptions, CalloutAction

NodeProperty(
    display_name="Info",
    name="info",
    type="callout",
    type_options=CalloutTypeOptions(
        callout_action=CalloutAction(
            type="openPreBuiltAgentsCollection",
            label="View Agents",
        )
    ),
    default="",
)
```

**Type Options:**
- `callout_action?: CalloutAction` - Action to perform when clicked

### 15. `'credentialsSelect'`
Credential selector dropdown.

```python
from app.schemas.node_property import NodeProperty

NodeProperty(
    display_name="Credential",
    name="credential",
    type="credentialsSelect",
    credential_types=["extends:oAuth2Api"],
    default="",
)
```

### 16. `'resourceLocator'`
Resource locator (for selecting resources from external services).

```python
from app.schemas.node_property import NodeProperty

NodeProperty(
    display_name="Resource",
    name="resource",
    type="resourceLocator",
    default={"mode": "id", "value": ""},
)
```

### 17. `'resourceMapper'`
Resource mapper (for mapping fields between systems).

```python
from app.schemas.node_property import NodeProperty, ResourceMapperTypeOptions

NodeProperty(
    display_name="Map Fields",
    name="fieldMapping",
    type="resourceMapper",
    type_options=ResourceMapperTypeOptions(
        resource_mapper={
            "mode": "map",
            "resourceMapperMethod": "getMappingFields",
        }
    ),
    default={},
)
```

**Type Options:**
- `resource_mapper?: Dict[str, Any]` - Configuration for resource mapping

### 18. `'filter'`
Filter/condition builder.

```python
from app.schemas.node_property import NodeProperty, FilterTypeOptions

NodeProperty(
    display_name="Filter",
    name="filter",
    type="filter",
    type_options=FilterTypeOptions(
        filter={
            "version": 1,
            "caseSensitive": True,
            "allowedCombinators": ["and", "or"],
            "maxConditions": 10,
        }
    ),
    default={},
)
```

**Type Options:**
- `filter?: Dict[str, Any]` - Filter configuration

### 19. `'assignmentCollection'`
Assignment collection (for variable assignments).

```python
from app.schemas.node_property import NodeProperty, AssignmentTypeOptions

NodeProperty(
    display_name="Assignments",
    name="assignments",
    type="assignmentCollection",
    type_options=AssignmentTypeOptions(
        assignment={
            "hideType": False,
            "defaultType": "string",
        }
    ),
    default={},
)
```

**Type Options:**
- `assignment?: Dict[str, Any]` - Assignment configuration

### 20. `'credentials'`
Credential configuration.

```python
from app.schemas.node_property import NodeProperty

NodeProperty(
    display_name="Credentials",
    name="credentials",
    type="credentials",
    credential_types=["myApi"],
    default={},
)
```

### 21. `'workflowSelector'`
Workflow selector (for selecting other workflows).

```python
from app.schemas.node_property import NodeProperty

NodeProperty(
    display_name="Workflow",
    name="workflow",
    type="workflowSelector",
    default="",
)
```

### 22. `'curlImport'`
cURL import field (for importing cURL commands).

```python
from app.schemas.node_property import NodeProperty

NodeProperty(
    display_name="cURL Command",
    name="curlCommand",
    type="curlImport",
    default="",
)
```

## Common Type Options

Many type options are shared across multiple property types:

### `multipleValues`
Allows multiple values for the property.

```python
from app.schemas.node_property import MultipleValuesOptions

type_options = MultipleValuesOptions(
    multiple_values=True,
    multiple_value_button_text="Add Another",  # Custom button text
)
```

### `display_options`
Conditionally show/hide properties based on other property values.

```python
from app.schemas.node_property import DisplayOptions

display_options = DisplayOptions(
    show={
        "operation": ["create", "update"],
    },
    hide={
        "resource": ["user"],
    },
)
```

### `required`
Mark a property as required.

```python
from app.schemas.node_property import NodeProperty

NodeProperty(
    display_name="Required Field",
    name="requiredField",
    type="string",
    required=True,
    default="",
)
```

## Example: ManualTrigger Node

The ManualTrigger node uses a simple `'notice'` type property:

```python
from app.schemas.node_property import NodeProperty

properties = [
    NodeProperty(
        display_name="This node is where the workflow execution starts (when you click the 'test' button on the canvas).<br><br> <a data-action=\"showNodeCreator\">Explore other ways to trigger your workflow</a> (e.g on a schedule, or a webhook)",
        name="notice",
        type="notice",
        default="",
    ),
]
```

## Using Example Properties

The `ExampleProperties` class in `app/schemas/node_property.py` provides static methods that return example property instances for each type:

```python
from app.schemas.node_property import ExampleProperties

# Get an example notice property
notice_prop = ExampleProperties.notice_property()

# Get an example string property
string_prop = ExampleProperties.string_property()

# Get an example options property
options_prop = ExampleProperties.options_property()
```

## References

- Schema definitions: `app/schemas/node_property.py`
- Node examples: `app/nodes/`
- Pydantic documentation: https://docs.pydantic.dev/
