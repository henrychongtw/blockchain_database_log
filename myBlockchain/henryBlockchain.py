import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request

import sqlite3
from json import dumps, loads


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

                # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n----------------\n")

            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            if not self.valid_proof(last_block['proof'], block['proof'],last_block_hash):
                return False

            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        #consensus Algorithm
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

    def new_block(self, proof, previous_hash):
        block = {'index' : len(self.chain) +1, 'timestamp':time(), 'transaction': self.current_transactions, 'proof': proof, 'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({'sender': sender,'recipient': recipient,'amount': amount,
        })

        return self.last_block['index']+1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        last_proof = last_block['proof']
        last_hash = self.hash(last_block)
        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        # guess = f'{last_proof}{proof}'.encode()
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
        #如果要調整演算法的難度，只需要更改尾端0的次數，但是4個0已經很夠



    def construct():
    	data = request.form['data']
    		# print data
    	data1 = loads(data)
    	conn, cursor = database_connect()
    	data1 = data_contruct_new(data1)
    	data1['pre_hash'] = get_pre_hash(cursor)
    	data1['nouce'] = call_nouce()
    	data1['hash'] = call_hash(data1)
    	conn.close()
    	return jsonpify(data1)


    def data_contruct_new(data1):
    	nouce = {"nouce":u""}
    	hash = {"hash":u""}
    	pre_hash =  {"pre_hash":u""}
    	data1.update(nouce)
    	data1.update(hash)
    	data1.update(pre_hash)
    	return data1



    def insert():
        data = request.form['data']
        data1 = loads(data)
        conn, cursor = database_connect()
        try:
            cursor.execute("insert into journal()")
            conn.commit()
            return "Success"
        except:
            return "Failed"
        conn.close()

    # # def insert():
    #   	data = request.form['data']
    #     # data1 = loads(data)
    #     # conn, cursor = database_connect()
    #    	try:
    #    		cursor.execute("insert into journal(journal_id, entry_date, create_time, created_by, post_status, account_code, amount, dr_cr, nouce, hash) values ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [ data1['journal_id'], data1['entry_date'], data1['create_time'], data1['created_by'], data1['post_status'], data1['account_code'], data1['amount'], data1['dr_cr'], data1['nouce'], data1['hash']])
    #    		conn.commit()
    #    		return "Success"
    #    	except:
    #    		return "Failed"
    #    	conn.close()


def database_connect():
    conn = sqlite3.connect('Blockchain.db')
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    return conn, cursor

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d



app = Flask(__name__)

node_identifier = str(uuid4()).replace('-','')

blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    # last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_block)

    blockchain.new_transaction(sender="0",recipient=node_identifier,amount=1,)

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof,previous_hash)

    response = {'message': "New Block Forged", 'index':block['index'], 'transaction': block['transaction'], 'proof':block['proof'], 'previous_hash': block['previous_hash'],}

    return jsonify(response), 200

@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {'chain': blockchain.chain, 'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {'message': 'New nodes have been added', 'total_nodes': list(blockchain.nodes),}

    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    conn, cursor = database_connect()

    if replaced:
        response = {'message': 'Local chain was replaced', 'new_chain': blockchain.chain}
    else:
        response = {'message': 'Local chain is authoritative', 'chain': blockchain.chain}

    count = cursor.execute("select count(*) from BLOCKS").fetchall()
    print(count)
    if count[0]['count(*)'] > 0:
        last_row = cursor.execute("select * from BLOCKS_FULL where ID = (select MAX(ID) from BLOCKS_FULL)").fetchall()
        tag = []
        for i in last_row:
            tag.append(i)
            ID = tag[0]['ID']
            index = tag[0]['INDEX_NO']
    else:
        ID = 0
        index = 0

    for i, data in enumerate(blockchain.chain) :
        if i < ID:
            continue
        # elif ID == 0:
        #     print(data)
        #     cursor.execute("insert into BLOCKS_FULL(ID, INDEX_NO, PRE_HASH, PROOF, TIMESTAMP, AMOUNT, RECIPIENT, SENDER) values (?,?,?,?,?,?,?,?)", [i, data['index'],  data['previous_hash'], data['proof'], data['timestamp'], 0, "Nan", 0])
        #     conn.commit()
        #     print("Success")
        else:
            try:
                print(data)
                print("==========")
                # print(data['transaction'][0]['sender'])
                cursor.execute("insert into BLOCKS_FULL(ID, INDEX_NO, PRE_HASH, PROOF, TIMESTAMP, AMOUNT, RECIPIENT, SENDER) values (?,?,?,?,?,?,?,?)", [i, data['index'],  data['previous_hash'], data['proof'], data['timestamp'], data['transaction'][0]['amount'], data['transaction'][0]['recipient'], data['transaction'][0]['sender']])
                conn.commit()
                print("Success")
            # return
            except:
                print("Failed")
    conn.close()
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
