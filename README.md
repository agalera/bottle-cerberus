# Cerberus plugin
Cerberus plugin for bottle

## installation

Via pip:
```pip install bottle-cerberus```

Or clone:
```git clone https://github.com/agalera/bottle-cerberus.git```


## example:
```python
from bottle import get, install, run
from bottle_cerberus import CerberusPlugin, Schema


class ExampleSchema(Schema):
    def schema(self):
        return {
            'ex': {'type': 'integer'},
            'url': {'ex': {'coerce': int}}
        }


class QuerySchema(Schema):
    def schema(self):
        return {'ex': {'coerce': int}}


@get('/cerberus/<ex>', schemas={'body': ExampleSchema(),
                                'query_string': QuerySchema())
def test_cerberus(ex):
    from bottle import request
    print("query_string", request.query['ex'], type(request.query['ex']))
    print("url", ex, type(ex))
    print("body", request.json.get('ex'), type(request.json.get('ex')))


install(CerberusPlugin())
run(host="0.0.0.0", port="9988")


```

# Schemas

## Optional keys

body: schema for request.json

url: schema for url (no query string)

query_string: schema for query strings

# Schema

Github Schema: https://github.com/nicolaiarocci/cerberus
Doc schema: http://docs.python-cerberus.org/en/stable/
