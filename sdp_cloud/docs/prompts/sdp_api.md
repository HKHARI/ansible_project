 - Code Structure
    - Have a seperate function to 
        - handle each API method
        - validate the payload
        - prepare the input_data from payload.
        - prepare the endpoint from module_name and id.
    - Go through the requirement fully and list out the plan to implement the module.
    - list all the task and get approval then proceed
 
 sdp_api.py is intended to do the following:
    - Parameters that are common to all modules
        - domain
        - portal_name
        - auth_token
        - client_id
        - client_secret
        - refresh_token
        - dc
        - parent_module_name : [requests, problems, changes]
        - child_module_name : [tasks, worklog, uploads, checklists]
        - grand_child_module_name : [comments, worklogs, uploads]
        - method : [GET, ADD, UPDATE, DELETE]
        - payload
        - parent_id
        - child_id
        - grand_child_id
    - Mandatory parameters
        - domain
        - portal_name
        - auth_token or {client_id, client_secret, refresh_token}
        - dc
        - parent_module_name
        - method
    - Mutually exclusive parameters
        - auth_token : client_id, client_secret, refresh_token
    - Required together parameters
        - [client_id, client_secret, refresh_token] 
        - if child_id is provided then parent_id is required
        - if grand_child_id is provided then child_id and parent_id is required
        - if child_module_name is provided then parent_module_name and parent_id is required
        - if grand_child_module_name is provided then child_module_name, child_id, parent_module_name and parent_id is required
    - Operation Map
        if id is provided and method is GET then GET SINGLE
        if payload is provided and method is GET then GET LIST
        if payload is provided and method is ADD then POST
        if id and payload is provided and method is UPDATE then PUT
        if id is provided and method is DELETE then DELETE
    - Operations that are common to all modules
        - GET LIST
            - General Structure of payload for GET LIST
                input_data : {
                    list_info : {
                        "row_count"         : number of rows to be returned(maximum row_count = 100)
                        "start_index"       : starting row index
                        "sort_field"        : "fieldName"
                        "sort_order"        : "asc/desc",
                        "get_total_count"   : boolean (by default it will be false)
                        "has_more_rows"     : boolean (will be returned with the response)
                        "total_count"       : count (will be returned with the response only)
                        "search_criteria"   :  Refer search criteria object given in the attributes of List Info(For performing advanced search)
                        "fields_required" : [ "list of fields required" ]
                    }
                }
            - Sample playbook format
                module_name: "requests"
                payload:
                    row_count: {val : <number>, default : 10, maximum : 100}
                    sort_field:{val :<allowed_sort_fields>, default : "created_date"}
                    sort_order: {val : [asc, desc], default : "asc"}
                    get_total_count: {val : [true, false], default : "false"}
            - Allowed Payload keys
                row_count
                sort_field
                sort_order
                get_total_count
            - Parent Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>
            - Child Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>/<child_module_name>
            - Grand Child Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>/<child_module_name>/<child_id>/<grand_child_module_name>
        - GET SINGLE
            - Parent Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>
            - Child Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>/<child_module_name>/<child_id>
            - Grand Child Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>/<child_module_name>/<child_id>/<grand_child_module_name>/<grand_child_id>
        - POST
            - Parent Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>              
            - Child Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>/<child_module_name>
            - Grand Child Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>/<child_module_name>/<child_id>/<grand_child_module_name>
        - PUT
            - Parent Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>
            - Child Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>/<child_module_name>/<child_id>
            - Grand Child Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>/<child_module_name>/<child_id>/<grand_child_module_name>/<grand_child_id>
        - DELETE
            - Parent Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>
            - Child Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>/<child_module_name>/<child_id>
            - Grand Child Entity format
                endpoint - <domain>/app/<portal>/api/v3/<parent_module_name>/<parent_id>/<child_module_name>/<child_id>/<grand_child_module_name>/<grand_child_id>
        - Payload Format for POST and PUT
            - Example
                - input_data = {
                    "request" : {
                        "subject" : "New Request from Ansible",
                        "description" : "Created via sdp_api module",
                        "requester" : {
                            "name" : "Administrator"
                        }
                    }
                }
        - Playbook Format for POST and PUT
            - Example   
                - module_name: "requests"
                - payload:
                    subject: "New Request from Ansible"
                    description: "Created via sdp_api module"
                    requester: "Administrator" 
                - method: "POST"
            - Allowed Payload keys and values structure
               - get the allowed_payload_fields from allowed_fields_config.py file and no other fields and nesting are allowed.
               - field_type_config, will have a key called type and based on field type the structure of the payload should be constructed.
                 - Example
                    - If field_type is string 
                        - Subject: "New Request from Ansible" 
                    - If field_type is number
                        - Priority: 1 
                    - If field_type is boolean
                        - IsEscalated: true 
                    - If field_type is datetime
                        - if value is timestamp 
                            reported_time: { 
                                "display_value": "Dec 22, 2024 11:54 PM",
                            }
                        - if value is milliseconds
                            reported_time: { 
                                "value": "1734891879761"
                            }
                    - If field_type is lookup
                        - Category: {"name": "Administrator"} 
                    - if field_type is user
                        - if value is string
                            Requester: {"name": "HK"} 
                        - if value is email id
                            Requester: {"email_id": "harish@manageengine.com"}
                    - if field_type is group
                        - create object with group_name and have field and value in it
                        - Example
                            - Playbook payload given
                                - is_known_error: true
                            - field config in allowed_fields_config.py
                                - "is_known_error": {"type": "boolean", "is_group_field": true, "group_name": "known_error_details"},
                                - For above config payload should be constructed as follows
                                    - known_error_details: {"is_known_error": "true"}
                    
        - Allowed fields Configuration
            - create <module_name>_fields_config.py file in module_utils and have 
                - allowed_sort_fields : It should have array fields that are supported for sorting for that module
                - allowed_payload_fields : It should have array fields that are supported for payload for that module
                - field_type_config : It should have fields with corresponding field types. If field type is group then it should have group_name key as well.
                    
            - Make use of this configuration to validate the payload before making API call.
        - API Request Structure
            - url = <domain>/app/<portal>/api/v3/<module_name>
            - method = <method>
            - headers = {
                    "Accept":"application/vnd.manageengine.sdp.v3+json",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": "Zoho-oauthtoken <auth_token>"
                };
            - input_date = <payload>
        

   
    


