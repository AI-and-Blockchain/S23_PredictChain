import sys
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

    # datasets.load_data("data/dow_jones_index/preprocessed.csv")

    handler = dataManager.LocalDataHandler("dow_jones_index", "time_step", "stock")

    model = models.PredictModel.create("MLP", "tom", handler, hidden_dim=5, num_hidden_layers=1)
    model.train_model(target_attrib="close", num_epochs=50, lookback=10, sub_split_value=0, plot_eval=True)


if __name__ == "__main__":
    # =============[NO CODE HERE OR BELOW]=============== #
    sandbox()
    # =================================================== #
