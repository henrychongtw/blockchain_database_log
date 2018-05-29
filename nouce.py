from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonpify

import random
app = Flask(__name__)
api = Api(app)


class nouce(Resource):
    def get(self):
        nouce = "%032x"% random.getrandbits(256)
        randomv = {'nouce': nouce}
        return jsonpify(randomv)

api.add_resource(nouce, '/nouce')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port='8001')
