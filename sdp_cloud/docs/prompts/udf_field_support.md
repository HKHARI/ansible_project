UDF FIELD HANDLING
- UDF field structure in input data
    - input_date {
        problem:{
            .....
            udf_fields: {
                <udf_field_name>: <udf_field_value>
                <udf_field_name>: <udf_field_value>
                ...
            }
        }
    }
- Rules
    - UDF field is not supported for child and grand child modules add and edit api
    - UDF field always starts with udf_ 
    - UDF field is always in lowercase. If payload have UDF field name in uppercase, it should be converted to lowercase.

   

- Need to find structure for the given udf field name 
    - Make a meta info call to get the udf field structure. 
    - URL : <domain>/app/<portal_name>/api/v3/<parent_module_name>/_metainfo
    - Response : 
        {
            metainfo: {
                ...
                fields: {
                    ...
                    udf_fields: {
                        ...
                        <udf_field_name>: {
                            ...
                            type: <udf_field_type>
                        }
                    }
                }
            }
        }
    - Make the meta info call to get the udf field structure once
    - Store the udf_fields: {...<udf_field_name>: {...type: <udf_field_type>}...} part alone in udf_field_config_cache.
    - If normal field then refer field config to get the type, if udf field then refer udf_field_config_cache to get the type.
    - Then the rest of the logic is same as normal field.
    - Instead of putting the udf field in the payload, we need to put the udf field in the udf_fields part of the payload.

- Write a implementation plan for the above logic and get approval for it and proceed.
- also have this implementation seperate util file. just call the module if udf field is present in the payload. and get the meta info call response and update the payload..
- Ensure followings
    - not to break any existing functionality.
    - to handle the edge cases.
    - to handle the error cases.
    - No code duplication.
    - Keep the code simple and readable.
