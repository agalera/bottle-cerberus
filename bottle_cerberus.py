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

    def config_to_dict(self, cfg, result=None):
        if isinstance(cfg, ConfigDict.Namespace):
            # initial dict
            if not result:
                result = {}

            for k in cfg:
                result[k] = self.config_to_dict(cfg[k], {})
            return result
        else:
            return cfg

    def apply(self, callback, route):
        schemas = self.config_to_dict(route.config.get(self.keyword, None))
        if not schemas:
            return callback
        validators = {k: MyValidator(schemas[k]) for k in schemas}

        @wraps(callback)
        def wrapper(*args, **kwargs):
            shortcut = {'url': kwargs,
                        'body': request.json or {},
                        'query_string': request.query}

            for k in validators:
                # modify original reference
                for k2, v in validators[k].normalized(shortcut[k]).items():
                    shortcut[k][k2] = v

                if not validators[k].validate(shortcut[k]):
                    raise HTTPError(400, "bad request")

            return callback(*args, **kwargs)

        return wrapper
