import abc
import functools
import bottle
import cerberus


class Schema(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def schema(self):
        pass


class MissingSchemaError(Exception):
    pass


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
                    k: v for k, v in iter(bottle.request.query)
                }
            }

            for k in validators:
                 # modify original reference
                shortcut[k] = validators[k].normalized(shortcut[k])

                if (shortcut[k] is None or
                        not validators[k].validate(shortcut[k])):
                    raise bottle.HTTPError(400, "bad request")

            return callback(*args, **kwargs)

        return wrapper
