from bottle import HTTPError, ConfigDict, request
from functools import wraps
from cerberus import Validator


class CerberusPlugin(object):
    name = 'CerberusPlugin'
    api = 2
    keyword = 'schema'

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
        schema = self.config_to_dict(route.config.get(self.keyword, None))
        if not schema:
            return callback
        validators = {k: Validator(schema[k]) for k in schema}

        @wraps(callback)
        def wrapper(*args, **kwargs):
            shortcut = {'url': kwargs,
                        'body': request.json or {},
                        'query_string': request.query}

            for k in validators:
                shortcut[k] = validators[k].normalized(shortcut[k])
                if not validators[k].validate(shortcut[k]):
                    raise HTTPError(400, "bad request")

            kwargs = shortcut['url']
            request.json = shortcut['body']
            request.query = shortcut['query_string']
            return callback(*args, **kwargs)

        return wrapper
