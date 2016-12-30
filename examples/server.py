from bottle import get, install, run
from cerberus_plugin import CerberusPlugin


@get("/example/<number>", schema={'url': {'number': {'coerce': int}}})
def example(number):
    return "the best number %s!" % number


install(CerberusPlugin())
run(host="0.0.0.0", port="9988")
