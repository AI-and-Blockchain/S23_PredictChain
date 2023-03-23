import dataclasses
import sys
from flask import Flask, request
import os
import json
import copy
sys.path.append("../")
import utils


with open(".creds/oracle_creds", "r") as file:
    SECRET = file.readline()

class Pricing:
    def calc_model_train_price(self, raw_model: str, data_size: str):
        # TODO: Pricing logic
        utils.transact(utils.ORACLE_ALGO_ADDRESS, SECRET, utils.ORACLE_ALGO_ADDRESS, 1,
                       note=f"{utils.OpCodes.UPDATE_PRICE}<ARG>:train<ARG>:{dataset_name}")
        return 0

    def calc_model_query_price(self, model: str):
        # TODO: Pricing logic
        return 0


class ClientTransactionMonitor(utils.TransactionMonitor):

    def process_incoming(self, txn):
        # Split into OP and ARGS
        data = txn["note"].split("<ARG>:")

        match data[0]:
            case utils.OpCodes.UP_DATASET:
                ...
            case utils.OpCodes.QUERY_MODEL:
                ...
            case utils.OpCodes.UPDATE_PRICE:
                ...


app = Flask(__name__)


@app.route('/model_train_price', methods=["GET"])
def report_model_train_price():
    return {"price": Pricing.calc_model_train_price(*)}

@app.route('/model_query_price', methods=["GET"])
def report_model_query_price():
    return {"price": Pricing.calc_model_query_price(*)}


if __name__ == '__main__':
    if os.path.isdir("oracle"):
        os.chdir("oracle")
    app.run()