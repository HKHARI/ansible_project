# Ansible Test Documentation
     
### Virtual Environment
    - Create a virtual environment
    ```bash
    $ python3 -m venv venv
    $ source venv/bin/activate
    ```
### Install Dependencies
    ```bash
    pip install ansible-core ansible-lint
    ```
### Sanity Test Collection
   
```bash
    $ cd {...}/ansible_Collections/{namespace}/{Collection_name}/ #navigate to Collection
    $ ansible-test sanity --docker default # if dependencies aren't installed [Recommended]

    #Specific Sanity Test
    $ ansible-test sanity   # run all sanity tests 
    $ ansible-test sanity plugins/modules/files/template.py # run against specified files
    $ ansible-test sanity --test validate-modules # only run a single sanity test
    $ ansible-test sanity --test validate-modules plugins/modules/files/template.py # run a single sanity test against a specified file
```
### lint Test Collection
   ```bash
   $ ansible-lint # Run Linter: Execute against the collection root.
   ``` 

###  Functionality (Integration)

- Define Targets: Ensure 'tests/integration/targets/' exists.
```bash
    ansible-test integration --docker default #(or your preferred target)
```
- Verify Outcome: Ensure tasks verify "success" states (idempotency).

