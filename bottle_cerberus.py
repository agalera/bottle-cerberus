from bottle import HTTPError, ConfigDict, request
from functools import wraps
from cerberus import Validator


class MyValidator(Validator):
    def _validate_type_objectid(*args, **kwargs):
        return True


class CerberusPlugin(object):
    name = 'CerberusPlugin'
    api = 2
    keyword = 'schemas'

    def apply(self, callback, route):
        schemas = {}
        for namespace in route.config:
            if self.keyword == namespace[:len(self.keyword)]:
                old = schemas
                final = namespace.split('.')[-1]
                for key in namespace.split('.')[1:]:
                    if key not in old:
                        if final == key:
                            old[key] = route.config[namespace]
                            continue
                        old[key] = {}
                    old = old[key]

        if schemas == {}:
            return callback

        validators = {k: MyValidator(schemas[k],
                                     allow_unknown=True) for k in schemas}

        @wraps(callback)
        def wrapper(*args, **kwargs):
            print("cerberus")
            shortcut = {'url': kwargs,
                        'body': request.json or {},
                        'query_string': {k: v for k, v in request.query.items()}}

            for k in validators:
                # modify original reference
                shortcut[k] = validators[k].normalized(shortcut[k])

                if shortcut[k] is None:
                    raise HTTPError(400, "bad request")

                if not validators[k].validate(shortcut[k]):
                    raise HTTPError(400, "bad request")

            return callback(*args, **kwargs)

        return wrapper
