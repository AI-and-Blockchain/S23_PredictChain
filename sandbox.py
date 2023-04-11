import json
import sys
import base64
import os
import datetime
import pandas as pd
from common import constants
from common import utils
from oracle import dataManager, models
import oracle.oracleCore as oracleCore
import client.clientCore as clientCore


def sandbox():
    """Wrapper function for any informal testing code"""
    oracleCore.OracleState.init()

    # datasets.load_data("data/dow_jones_index/preprocessed.csv")

    # handler = dataManager.LocalDataHandler("dow_jones_index", "time_step", "stock")

    # model = models.PredictModel.create("GRU", "tom", handler, hidden_dim=5, num_hidden_layers=1)
    # model.train_model(target_attrib="close", num_epochs=50, lookback=10, sub_split_value=0, plot_eval=True)

    # link = "https://matthew-misc-bucket.s3.amazonaws.com/datasets/dow_jones_index.csv"
    # dataManager.save_dataset("local", "dow_jones_index", link, "0txn", "0user", "time_step", sub_split_attrib="stock")

    """mock_txn = {"id": "0txn", "sender": "0user", "amount": float("inf"), "note": base64.b64encode(json.dumps({
        "op": utils.OpCodes.TRAIN_MODEL, "ds_name": "dow_jones_index", "raw_model": "GRU", "trained_model": "test",
        "hidden_dim": 5, "num_hidden_layers": 1
    }).encode())}"""

    note = {
        "op": utils.OpCodes.TRAIN_MODEL,
        "ds_name": "dow_jones_index",
        "raw_model": "GRU",
        "trained_model": "testModel",
        "hidden_dim": 5,
        "num_hidden_layers": 1,
        "num_epochs": 3,
        "target_attrib": "close"
    }
    mock_txn = {"id": "0txn", "sender": "0user", "payment-transaction": {"amount": float("inf")},
                "note": base64.b64encode(json.dumps(note).encode())}

    oracleCore.OracleState.monitor.process_incoming(mock_txn)


if __name__ == "__main__":
    # =============[NO CODE HERE OR BELOW]=============== #
    sandbox()
    # =================================================== #
