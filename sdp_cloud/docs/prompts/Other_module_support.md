parent_module_name should be validated based on sdpconfig. 

- config should be restructured like this
- No need for singular just use the key singlar key and strict with that also change the places where we used this

<Singlar_moudle_name> : {
    endpoint : <endpoint>,
    children : {
        <child_moudule_singilar_name> : {
            endpoint : <endpoint>
            children : {}
        }
    }
}