# Ansible Collection for ManageEngine ServiceDesk Plus Cloud

The Ansible Collection for [ManageEngine ServiceDesk Plus Cloud](https://www.manageengine.com/products/service-desk/) provides Ansible content that enables users to automate the management of ITSM processes such as requests, problems, changes, and releases.

## Description

This collection is ideal for IT administrators, DevOps engineers, and automation specialists who work with ServiceDesk Plus Cloud and want to integrate its capabilities into their infrastructure automation workflows.

## Requirements

- **Ansible-Core**: >= 2.15.0
- **Python**: >= 3.6
- No additional Python libraries are required.
- A ServiceDesk Plus Cloud instance and OAuth credentials are required for module authentication.

## Installation

Before using this collection, you need to install it with the Ansible Galaxy command-line tool:

```bash
ansible-galaxy collection install manageengine.sdp_cloud
```

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
collections:
  - name: manageengine.sdp_cloud
```

To upgrade the collection to the latest available version, run the following command:

```bash
ansible-galaxy collection install manageengine.sdp_cloud --upgrade
```

You can also install a specific version of the collection. Use the following syntax to install version 1.0.0:

```bash
ansible-galaxy collection install manageengine.sdp_cloud:==1.0.0
```

See [using Ansible collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for more details.

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

## Use Cases

Here are a few common automation scenarios enabled by this collection:

1.  **Request Management**: Automatically create, update, and query requests during CI/CD pipelines or event-driven automation.
2.  **Problem Management**: Trigger problem records and manage their lifecycle in coordination with incident resolution.
3.  **Change Management**: Automate the creation and update of change requests during system patching or upgrades.
4.  **Release Management**: Automate release planning and deployment tracking.

## Modules

| Name | Description |
| ---- | ----------- |
| [oauth_token](https://github.com/HKHARI/AnsibleCollections/blob/main/manageengine/sdp_cloud/plugins/modules/oauth_token.py) | Generate ManageEngine SDP Cloud OAuth Access Token |
| [read_record](https://github.com/HKHARI/AnsibleCollections/blob/main/manageengine/sdp_cloud/plugins/modules/read_record.py) | Read API module for ManageEngine ServiceDesk Plus Cloud |
| [write_record](https://github.com/HKHARI/AnsibleCollections/blob/main/manageengine/sdp_cloud/plugins/modules/write_record.py) | Manage records (create, update, delete) in ManageEngine ServiceDesk Plus Cloud |

## Example Usage

### Configuration
To securely manage your API credentials, we recommend using a `credentials.yml` file (excluded from version control) or environment variables.

**`credentials.yml` template:**
```yaml
---
client_id: "YOUR_CLIENT_ID"
client_secret: "YOUR_CLIENT_SECRET"
refresh_token: "YOUR_REFRESH_TOKEN"
dc: "US" # Data Center (US, EU, IN, AU, CN, JP)
```

### Playbook Examples

**Generate Token:**
```yaml
- name: Fetch OAuth Token
  manageengine.sdp_cloud.oauth_token:
    client_id: "{{ client_id }}"
    client_secret: "{{ client_secret }}"
    refresh_token: "{{ refresh_token }}"
    dc: "{{ dc }}"
  register: auth_token
```

**Get Request Details:**
```yaml
- name: Get Request Details
  manageengine.sdp_cloud.read_record:
    domain: "sdpondemand.manageengine.com"
    parent_module_name: "request"
    parent_id: "100"
    auth_token: "{{ auth_token.access_token }}"
    dc: "{{ dc }}"
    portal_name: "ithelpdesk"
```

**Create a Problem:**
```yaml
- name: Create a Problem
  manageengine.sdp_cloud.write_record:
    auth_token: "{{ auth_token.access_token }}"
    dc: "{{ dc }}"
    domain: "sdpondemand.manageengine.com"
    portal_name: "ithelpdesk"
    parent_module_name: "problem"
    payload:
      title: "Network Latency Issue"
      description: "Users reporting slow access to file server"
      urgency: "High"
      impact: "High"
```

**Update a Problem:**
```yaml
- name: Update a Problem
  manageengine.sdp_cloud.write_record:
    auth_token: "{{ auth_token.access_token }}"
    dc: "{{ dc }}"
    domain: "sdpondemand.manageengine.com"
    portal_name: "ithelpdesk"
    parent_module_name: "problem"
    parent_id: "100"
    payload:
      title: "Updated Title"
      priority: "High"
```

**Create a Release:**
```yaml
- name: Create a Release
  manageengine.sdp_cloud.write_record:
    auth_token: "{{ auth_token.access_token }}"
    dc: "{{ dc }}"
    domain: "sdpondemand.manageengine.com"
    portal_name: "ithelpdesk"
    parent_module_name: "release"
    payload:
      title: "Q3 Application Release"
      description: "Rolling out new features for Q3"
      priority: "Normal"
```

**Delete a Problem:**
```yaml
- name: Delete a Problem
  manageengine.sdp_cloud.write_record:
    auth_token: "{{ auth_token.access_token }}"
    dc: "{{ dc }}"
    domain: "sdpondemand.manageengine.com"
    portal_name: "ithelpdesk"
    parent_module_name: "problem"
    parent_id: "100"
    state: absent
```

## Testing

This collection is tested with:
- Ansible-Core >= 2.15.0
- Python 3.9+
- ServiceDesk Plus Cloud

## Contributing

We welcome contributions! Please feel free to open an issue or submit a pull request on the repository.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

As Red Hat Ansible Certified Content, this collection is entitled to support through the Ansible Automation Platform (AAP) using the **Create issue** button on the top right corner. If a support case cannot be opened with Red Hat and the collection has been obtained either from Galaxy or GitHub, there may community help available on the [Ansible Forum](https://forum.ansible.com/).

You can also contact SDP Cloud support at <servicedeskplus-cloud-support@manageengine.com>.

## Release Notes and Roadmap

For the latest changes, please refer to the [Changelogs](https://github.com/HKHARI/AnsibleCollections/blob/main/manageengine/sdp_cloud/changelogs/changelog.yaml) or GitHub Releases.

## Related Information

- [ManageEngine ServiceDesk Plus Cloud](https://www.manageengine.com/products/service-desk/)
- [Ansible Collection Documentation](https://docs.ansible.com/ansible/latest/collections/index.html)

## License Information

This collection is licensed under the GNU General Public License v3.0 or later.
See: [LICENSE](LICENSE)
