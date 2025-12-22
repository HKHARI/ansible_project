# ManageEngine ServiceDesk Plus Cloud Ansible Collection

The `manageengine.sdp_cloud` collection includes modules to interact with the ManageEngine ServiceDesk Plus Cloud API.

## Description

This collection allows you to manage Requests, Problems, Changes, and Request Tasks in ServiceDesk Plus Cloud. It supports creating, updating, retrieving details, and listing records.

## Requirements

- Python 3.6+
- Ansible 2.9+

## Authentication

All modules generally require the following authentication parameters:

- `domain`: The domain of your SDP Cloud instance (e.g., `sdpondemand.manageengine.com`).
- `portal_name`: The name of the portal (e.g., `ithelpdesk`).
- OAuth Credentials:
    - `client_id`
    - `client_secret`
    - `refresh_token`
    - `dc` (Data Center: US, EU, IN, AU, CN, JP, CA, SA)

Alternatively, you can provide a valid `auth_token` directly (not recommended for playbooks due to token expiration).

## Available Modules

| Module | Description |
| --- | --- |
| `write_request` | Create or Update Requests |
| `read_request` | Get Request details or list Requests |
| `write_problem` | Create or Update Problems |
| `read_problem` | Get Problem details or list Problems |
| `write_change` | Create or Update Changes |
| `read_change` | Get Change details or list Changes |
| `write_request_task` | Create or Update Request Tasks |
| `read_request_task` | Get Request Task details or list Tasks |
| `write_record` | Generic module for writing records |
| `read_record` | Generic module for reading records |

## Usage Examples

### Create a Request
```yaml
- name: Create Request
  manageengine.sdp_cloud.write_request:
    domain: "sdpondemand.manageengine.com"
    portal_name: "ithelpdesk"
    client_id: "..."
    client_secret: "..."
    refresh_token: "..."
    dc: "US"
    payload:
      subject: "Issue with VPN"
      status: "Open"
```

### Update a Request
```yaml
- name: Update Request
  manageengine.sdp_cloud.write_request:
    domain: "sdpondemand.manageengine.com"
    portal_name: "ithelpdesk"
    parent_id: "105"
    client_id: "..."
    client_secret: "..."
    refresh_token: "..."
    dc: "US"
    payload:
      status: "On Hold"
```

### Add a Task to a Request
```yaml
- name: Add Task
  manageengine.sdp_cloud.write_request_task:
    domain: "sdpondemand.manageengine.com"
    portal_name: "ithelpdesk"
    parent_id: "105"
    client_id: "..."
    client_secret: "..."
    refresh_token: "..."
    dc: "US"
    payload:
      title: "Check Logs"
      status: "Open"
```
