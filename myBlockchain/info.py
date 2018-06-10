import sqlite3
from flask_restful import Resource, reqparse

class Data(Resource):
    TABLE_NAME = 'info'

    def __init__(self, _id, previous_hash, proof,timestamp):
        self.id = _id
        self.previous_hash = previous_hash
        self.proof = proof
        self.timestamp = timestamp
        # self.transaction =transaction

    @classmethod
    def find_by_id(cls, _id):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM {table} WHERE id=?".format(table=cls.TABLE_NAME)
        result = cursor.execute(query, (_id,))
        row = result.fetchone()
        if row:
            user = cls(*row)
        else:
            user = None

        connection.close()
        return user


class InfoRegister(Resource):
    TABLE_NAME = 'info'

    parser = reqparse.RequestParser()
    parser.add_argument('_id',
        type=int,
        required=True,
        help="This field cannot be left blank!"
    )
    parser.add_argument('previous_hash',
        type=str,
        required=True,
        help="This field cannot be left blank!"
    )
    parser.add_argument('proof',
        type=int,
        required=True,
        help="This field cannot be left blank!"
    )
    parser.add_argument('timestamps',
        type=float,
        required=True,
        help="This field cannot be left blank!"
    )

    def post(self):
        data = InfoRegister.parser.parse_args()

        if Data.find_by_id(data['_id']):
            return {"message": "User with that username already exists."}, 400

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "INSERT INTO {table} VALUES (NULL, ?, ?,?)".format(table=self.TABLE_NAME)
        cursor.execute(query, (data['_id'], data['previous_hash'], data['proof'], data['timestamps']))

        connection.commit()
        connection.close()

        return {"message": "Info created successfully."}, 201
