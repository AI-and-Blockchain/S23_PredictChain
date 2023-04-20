import json
import sys
import base64
import os
import datetime
import pandas as pd
from common import constants
from common import utils
from oracle import dataManager, models, datasets
import oracle.oracleCore as oracleCore
import client.clientCore as clientCore


DEFAULT_USER_ID = "V5DGWVP6MUKMT5MFVOOELPSARVL5OLBIFTUITOOWQ4OA3RBPU2QJBKNPTQ"
DEFAULT_TXN_ID = "2DXP26ZTEZXUKL6FHUBWHM6NI3R32IOEOUZGC75TBIRKB4D4TODA"
DEFAULT_AMNT = 1000000000000000

def sim_transaction(command: dict, txn_id=DEFAULT_TXN_ID, user_id=DEFAULT_USER_ID, amount=DEFAULT_AMNT):
    """Simulates a transaction coming from the client to the oracle

    :param command: The command that the transaction will tell the oracle to execute
    :param txn_id: The id of the simulated transaction
    :param user_id: The id of the simulated sender of the transaction
    :param amount: The amount of micro-algo to give the transaction"""

    mock_txn = {"id": txn_id, "sender": user_id, "payment-transaction": {"amount": amount},
                "note": base64.b64encode(json.dumps(command).encode())}

    oracleCore.OracleState.monitor.process_incoming(mock_txn)


def sim_up_dataset(ds_name: str, ds_link: str, ds_size: int, time_attrib: str, endpoint="", sub_split_attrib="",
                        txn_id=DEFAULT_TXN_ID, user_id=DEFAULT_USER_ID, amount=DEFAULT_AMNT):
    """Simulates an upload dataset transaction

    :param ds_name: The name that will be assigned to the new dataset
    :param ds_link: The URL that links to the dataset.  This URL must yield a stream of bytes upon GET
    :param ds_size: The size of the dataset
    :param time_attrib: The attribute of the data that denotes the passage of time
    :param endpoint: The name of the endpoint that is associated with the dataset
    :param sub_split_attrib: The attribute that is used to split the dataset into independent subsets
    :param txn_id: The id of the simulated transaction
    :param user_id: The id of the simulated sender of the transaction
    :param amount: The amount of micro-algo to give the transaction"""

    command = {"op": utils.OpCodes.UP_DATASET, "ds_name": ds_name, "ds_link": ds_link, "ds_size": ds_size,
               "time_attrib": time_attrib, "endpoint": endpoint, "sub_split_attrib": sub_split_attrib}
    sim_transaction(command, txn_id, user_id, amount)


def sim_train_model(raw_model: str, trained_model: str, ds_name: str, num_epochs: int, target_attrib: str, hidden_dim: int,
                    num_hidden_layers: int, time_lag=1, training_lookback=2, sub_split_value=None, txn_id=DEFAULT_TXN_ID, user_id=DEFAULT_USER_ID, amount=DEFAULT_AMNT):
    """Simulates a train model transaction

    :param raw_model: The raw model to train
    :param trained_model: The name of the new trained model
    :param ds_name: The name of the dataset to train the model on
    :param num_epochs: The number of epochs to train the model for
    :param target_attrib: The name of the attribute that is used to test
    :param hidden_dim: The size of the hidden layers
    :param num_hidden_layers: The number of hidden layers
    :param time_lag: The time lag between the input and output sequences
    :param training_lookback: The size of the sliding time window to give to recurrent models
    :param sub_split_value: The value used to split the data along the saved sub_split attribute
    :param txn_id: The id of the simulated transaction
    :param user_id: The id of the simulated sender of the transaction
    :param amount: The amount of micro-algo to give the transaction"""

    command = {"op": utils.OpCodes.TRAIN_MODEL, "raw_model": raw_model, "trained_model": trained_model, "ds_name": ds_name,
               "num_epochs": num_epochs, "target_attrib": target_attrib, "hidden_dim": hidden_dim,
               "num_hidden_layers": num_hidden_layers, "time_lag": time_lag, "training_lookback": training_lookback,
               "sub_split_value": sub_split_value}
    sim_transaction(command, txn_id, user_id, amount)


def sim_query_model(trained_model: str, model_input: list, txn_id=DEFAULT_TXN_ID, user_id=DEFAULT_USER_ID, amount=DEFAULT_AMNT):
    """Simulates a query model transaction

    :param trained_model: The trained model to query
    :param model_input: The input to the trained model
    :param txn_id: The id of the simulated transaction
    :param user_id: The id of the simulated sender of the transaction
    :param amount: The amount of micro-algo to give the transaction"""

    command = {"op": utils.OpCodes.QUERY_MODEL, "trained_model": trained_model, "model_input": model_input}
    sim_transaction(command, txn_id, user_id, amount)


def sandbox():
    """Wrapper function for any informal testing code"""
    oracleCore.OracleState.init()

    ds_name = "dow_jones_index2"
    model_name = "testModel2"

    model_query = [
            [1, 0, 56, 16.98, 17.15, 15.96, 16.68, 132981863, -1.76678, 66.17769355, 80023895, 16.81, 16.58, -1.36823, 76, 0.179856],
            [1, 0, 63, 16.81, 16.94, 16.13, 16.58, 109493077, -1.36823, -17.66315005, 132981863, 16.58, 16.03, -3.31725, 69, 0.180941],
            [1, 0, 70, 16.58, 16.75, 15.42, 16.03, 114332562, -3.31725, 4.419900447, 109493077, 15.95, 16.11, 1.00313, 62, 0.187149]
    ]

    # Simulate the dataset upload portion of the service
    # sim_up_dataset(ds_name, "https://matthew-misc-bucket.s3.amazonaws.com/datasets/dow_jones_index.csv", 420, "time_step", sub_split_attrib="stock")

    # Simulate the model training part of the service
    sim_train_model("mlp", model_name, ds_name, 70, "close", 5, 1, time_lag=0, training_lookback=10, sub_split_value=0)

    # Simulate the model query portion of the service
    sim_query_model(model_name, model_query)


if __name__ == "__main__":
    # =============[NO CODE HERE OR BELOW]=============== #
    sandbox()
    # =================================================== #
