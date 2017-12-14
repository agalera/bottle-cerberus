import abc
import json
import functools

import bottle
import cerberus


JSON_CONTENT_TYPE = 'application/json'


class Schema(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def schema(self):
        pass


class MissingSchemaError(Exception):
    pass


class JSONError(bottle.HTTPResponse):
    def __init__(self, status, body):
        super(JSONError, self).__init__(json.dumps(body), status)
        self.content_type = 'application/json'


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
                            if not isinstance(route.config[namespace], Schema):
                                raise MissingSchemaError(
                                    "Missing Schema class")
                            old[key] = route.config[namespace].schema()
                            continue
                        old[key] = {}
                    old = old[key]

        if schemas == {}:
            return callback

        validators = {
            k: cerberus.Validator(
                schemas[k], allow_unknown=True) for k in schemas
        }

        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            shortcut = {
                'url': kwargs,
                'body': bottle.request.json or {},
                'query_string': {
                    k: v for k, v in bottle.request.query.items()
                }
            }

            for k in validators:
                # modify original reference
                shortcut[k] = validators[k].normalized(shortcut[k])

                if (shortcut[k] is None or
                        not validators[k].validate(shortcut[k])):

                    status = 400
                    body = validators[k].errors

                    if JSON_CONTENT_TYPE in bottle.request.content_type:
                        raise JSONError(status, body)
                    else:
                        raise bottle.HTTPError(status, body)

            return callback(*args, **kwargs)

        return wrapper
