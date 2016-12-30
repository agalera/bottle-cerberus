# Currently under development, unstable version!
# Cerberus plugin
Cerberus plugin for bottle

## installation

Via pip:
```pip install bottle-cerberus```

Or clone:
```git clone https://github.com/kianxineki/bottle-cerberus.git```


## example:
```python
from bottle import get, install, run
from cerberus_plugin import CerberusPlugin


@get("/example/<number>", schema={'url': {'number': {'coerce': int}}})
def example(number):
    return "the best number %s!" % number


install(CerberusPlugin())
run(host="0.0.0.0", port="9988")

```
