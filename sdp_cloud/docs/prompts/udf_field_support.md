# UDF FIELD HANDLING

## UDF Field Structure in Input Data
```json
{
    "problem": {
        "udf_fields": {
            "<udf_field_name>": "<udf_field_value>",
            "<udf_field_name>": "<udf_field_value>"
        }
    }
}
```

## Rules
- UDF fields are **not supported** for child and grandchild modules in ADD and EDIT APIs.
- UDF fields always start with `udf_`.
- UDF fields are strictly **lowercase**. If the payload contains uppercase UDF field names, they should be converted to lowercase.

## Implementation Details

### 1. Fetch UDF Metadata
To determine the structure and type of a given UDF field, perform a metadata call.

**URL:**
`<domain>/app/<portal_name>/api/v3/<parent_module_name>/_metainfo`

**Response Structure:**
```json
{
    "metainfo": {
        "fields": {
            "udf_fields": {
                "<udf_field_name>": {
                    "type": "<udf_field_type>"
                }
            }
        }
    }
}
```

### 2. Logic Flow
1.  **Fetch Metadata:** Make the `_metainfo` call once to retrieve the UDF field structure.
2.  **Cache Configuration:** Extract and store the `udf_fields` object (containing field names and types) in a local cache or variable (`udf_field_config_cache`).
3.  **Type Resolution:**
    *   For **normal fields**, refer to the static field configuration to determine the type.
    *   For **UDF fields**, refer to the `udf_field_config_cache`.
4.  **Payload Construction:**
    *   Process field values based on their type logic (same as normal fields).
    *   Place processed UDF fields inside a `udf_fields` nested object within the main payload, rather than at the root level.

## Requirements
- **Plan First:** Write an implementation plan for this logic and get approval before coding.
- **Modularize:** Implement this logic in a separate utility module/file. Call this utility only if UDF fields are present in the payload.
- **Goals:**
    - Do not break existing functionality.
    - Handle edge cases.
    - Handle error cases gracefully.
    - Avoid code duplication.
    - Keep the code simple and readable.
