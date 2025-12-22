# Support for Other Modules

Support the following modules with the existing framework:
- Request
- Problem
- Change

## Configuration Validation
`parent_module_name` should be validated based on `sdp_config`.

### Configuration Restructuring
- The configuration should be restructured to use **singular module names** as keys.
- Enforce strict usage of singular keys.
- Update all references in the codebase to match this structure.

**Proposed Structure:**
```python
<Singular_module_name> : {
    "endpoint" : "<endpoint>",
    "children" : {
        "<child_module_singular_name>" : {
            "endpoint" : "<endpoint>",
            "children" : {}
        }
    }
}
```