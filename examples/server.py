from bottle import get, install, run
from cerberus_plugin import CerberusPlugin


@get('/cerberus/<ex>', schemas={'body': {'ex': {'type': 'integer'}},
                                'url': {'ex': {'coerce': int}},
                                'query_string': {'ex': {'coerce': int}}})
def test_cerberus(ex):
    from bottle import request
    print("query_string", request.query['ex'], type(request.query['ex']))
    print("url", ex, type(ex))
    print("body", request.json.get('ex'), type(request.json.get('ex')))


install(CerberusPlugin())
run(host="0.0.0.0", port="9988")
