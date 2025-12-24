# SDP API Module Structure

## Code Structure
- **Modular Functions:**
    - Handle each API method.
    - Validate the payload.
    - Prepare `input_data` from the payload.
    - Construct the endpoint from `module_name` and `id`.
- **Process:**
    - Fully review requirements.
    - Plan implementation steps.
    - List tasks and get approval before proceeding.

`sdp_api.py` is intended to handle the core logic for the Ansible modules.

## Parameters

### Common Parameters
- `domain`
- `portal_name`
- `auth_token`
- `client_id`
- `client_secret`
- `refresh_token`
- `dc`
- `parent_module_name`: [requests, problems, changes]
- `child_module_name`: [tasks, worklog, uploads, checklists]
- `grand_child_module_name`: [comments, worklogs, uploads]
- `method`: [GET, ADD, UPDATE, DELETE]
- `payload`
- `parent_id`
- `child_id`
- `grand_child_id`

### Mandatory Parameters
- `domain`
- `portal_name`
- `auth_token` OR {`client_id`, `client_secret`, `refresh_token`}
- `dc`
- `parent_module_name`
- `method`

### Mutually Exclusive Parameters
- `auth_token` vs. (`client_id`, `client_secret`, `refresh_token`)

### Required Together Parameters
- `[client_id, client_secret, refresh_token]`
- If `child_id` is provided -> `parent_id` is required.
- If `grand_child_id` is provided -> `child_id` and `parent_id` are required.
- If `child_module_name` is provided -> `parent_module_name` and `parent_id` are required.
- If `grand_child_module_name` is provided -> `child_module_name`, `child_id`, `parent_module_name`, and `parent_id` are required.

## Operation Map
- **GET SINGLE**: `id` provided + `method` = GET
- **GET LIST**: `payload` provided + `method` = GET
- **POST**: `payload` provided + `method` = ADD
- **PUT**: `id` + `payload` provided + `method` = UPDATE
- **DELETE**: `id` provided + `method` = DELETE

## API Operations

### GET LIST
**General Payload Structure:**
```json
{
    "input_data": {
        "list_info": {
            "row_count": "number of rows (max 100)",
            "start_index": "starting row index",
            "sort_field": "fieldName",
            "sort_order": "asc/desc",
            "get_total_count": "boolean (default: false)",
            "has_more_rows": "boolean (response only)",
            "total_count": "count (response only)",
            "search_criteria": "Search criteria object",
            "fields_required": ["list of fields"]
        }
    }
}
```

**Ansible Playbook Format:**
```yaml
module_name: "requests"
payload:
    row_count: 10
    sort_field: "created_date"
    sort_order: "asc"
    get_total_count: false
```

### Endpoints
*   **Parent Entity:** `<domain>/app/<portal>/api/v3/<parent_module_name>`
*   **Child Entity:** `<domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>/<child_module_name>`
*   **Grandchild Entity:** `<domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>/<child_module_name>/<child_id>/<grand_child_module_name>`

### GET SINGLE, PUT, DELETE
Endpoints follow the same hierarchy but include IDs for specific resources (e.g., `.../<parent_id>`).

### POST & PUT Payload Format
**Example Input Data:**
```json
{
    "input_data": {
        "request": {
            "subject": "New Request from Ansible",
            "description": "Created via sdp_api module",
            "requester": {
                "name": "Administrator"
            }
        }
    }
}
```

**Ansible Playbook Format:**
```yaml
module_name: "requests"
payload:
    subject: "New Request from Ansible"
    description: "Created via sdp_api module"
    requester: "Administrator"
method: "POST"
```

## Field Configuration
**File:** `<module_name>_fields_config.py` in `module_utils`

Structure:
*   `allowed_sort_fields`: Array of fields supported for sorting.
*   `allowed_payload_fields`: Array of fields supported for payload.
*   `field_type_config`: Dictionary mapping fields to types (and `group_name` for grouped fields).

**Field Logic Examples:**
- **String:** `Subject: "My Request"`
- **Number:** `Priority: 1`
- **Boolean:** `IsEscalated: true`
- **DateTime:**
    - Timestamp: `reported_time: {"value": "1734891879761"}`
    - Strings: `reported_time: {"display_value": "Dec 22, 2024 11:54 PM"}`
- **Lookup:** `Category: {"name": "Administrator"}`
- **User:**
    - Name: `Requester: {"name": "HK"}`
    - Email: `Requester: {"email_id": "user@example.com"}`
- **Group:**
    - Playbook: `is_known_error: true`
    - Config: `"is_known_error": {"type": "boolean", "group_name": "known_error_details"}`
    - Result Payload: `known_error_details: {"is_known_error": "true"}`

## API Request Construction
1.  **URL**: `<domain>/app/<portal>/api/v3/<module_name>`
2.  **Method**: GET, POST, PUT, DELETE
3.  **Headers**:
    ```json
    {
        "Accept": "application/vnd.manageengine.sdp.v3+json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Zoho-oauthtoken <auth_token>"
    }
    ```
4.  **Data**: `input_data=<payload>`
