# ManageEngine SDP Cloud Ansible Collection

This collection provides Ansible modules to interact with ManageEngine ServiceDesk Plus Cloud ITSM. It allows you to automate various tasks such as managing requests, problems, and other ITSM entities via the SDP Cloud API.

## Collection Information

- **Namespace**: `manageengine`
- **Name**: `sdp_cloud`
- **Version**: `1.0.0`
- **Authors**: 
  - Harish Kumar <harishkumar.k@zohocorp.com>
  - Bharath B <bharath.baskaran@zohocorp.com>

## Installation

### From Source
1. Clone this repository:
   ```bash
   git clone https://github.com/HKHARI/AnsibleCollections.git
   ```
2. Navigate to the collection directory:
   ```bash
   cd AnsibleCollections/manageengine/sdp_cloud
   ```
3. Build and install the collection:
   ```bash
   ansible-galaxy collection build
   ansible-galaxy collection install manageengine-sdp_cloud-1.0.0.tar.gz
   ```

## Configuration

### Credentials
To securely manage your API credentials, create a `credentials.yml` file in your playbooks directory. **Do not commit this file to version control.**

**`credentials.yml` template:**
```yaml
---
client_id: "YOUR_CLIENT_ID"
client_secret: "YOUR_CLIENT_SECRET"
refresh_token: "YOUR_REFRESH_TOKEN"
dc: "US" # Data Center (US, EU, IN, AU, CN, JP)
```

### Usage in Playbooks
Import the credentials file in your playbooks using `vars_files`:

```yaml
- hosts: localhost
  vars_files:
    - credentials.yml
  tasks:
    # ...
```

## Modules

### 1. `oauth_token`
Generates an OAuth access token using the refresh token.

**Example:**
```yaml
- name: Fetch OAuth Token
  manageengine.sdp_cloud.oauth_token:
    client_id: "{{ client_id }}"
    client_secret: "{{ client_secret }}"
    refresh_token: "{{ refresh_token }}"
    dc: "{{ dc }}"
  register: auth_token
```

### 2. `read_record`
A generic module to retrieve data from SDP Cloud entities (Requests, Problems, Changes, etc.).

**Example: Get Request Details**
```yaml
- name: Get Request Details
  manageengine.sdp_cloud.read_record:
    domain: "sdpondemand.manageengine.com"
    parent_module_name: "requests"
    parent_id: "100"
    # ... credentials ...
```

### 3. `write_record`
A generic module to perform state-changing operations (POST, PUT, DELETE) on SDP Cloud entities.

**Features:**
- **Automatic Payload Construction**: Converts flat playbook variables into complex nested JSON structures required by the API.
- **Strict Validation**: Enforces type checking (String, Number, Boolean) and rejects invalid inputs.
- **Smart Field Handling**: Automatically handles `lookup` fields (resolves names), `user` fields (resolves emails/names), and `datetime` fields.
- **Error Reporting**: Provides detailed error messages including the raw API response.

**Example: Creating a Problem**
```yaml
- name: Create a Problem
  manageengine.sdp_cloud.write_record:
    auth_token: "{{ auth_token.access_token }}"
    dc: "{{ dc }}"
    module_name: "problems"
    method: "POST"
    payload:
      title: "Network Latency Issue"
      description: "Users reporting slow access to file server"
      urgency: "High"        # Lookup field
      impact: "High"         # Lookup field
      reported_by: "admin@org.com" # User field (email)
      is_known_error: true   # Boolean (automatically grouped if configured)
  register: problem_response
```

## Directory Structure
```
.
├── README.md
├── sdp_cloud/
│   ├── galaxy.yml
│   ├── plugins/
│   │   ├── modules/
│   │   │   ├── oauth_token.py
│   │   │   ├── read_record.py
│   │   │   └── write_record.py
│   │   └── module_utils/
│   │       ├── sdp_api.py
│   │       ├── sdp_config.py
│   │       ├── oauth.py
│   │       ├── requests_fields_config.py
│   │       └── problems_fields_config.py
│   └── playbooks/
│       ├── generate_token.yml
│       └── credentials.yml (Excluded from git)
```

## License
GPL-3.0-or-later
