import io
import abc
import json

import requests
import os
import pandas as pd

from oracle import dataManager


class DataHandler:
    """Manages the saving and usage of datasets"""

    SAVE_MODE = 0
    LOAD_MODE = 1
    env = ""

    def __init__(self, dataset_name: str, time_attrib: str, sub_split_attrib=""):
        """Manages the saving and usage of datasets

        :param dataset_name: The name of the dataset
        :param time_attrib: The attribute of the dataset that measures the passage of time.  This is important for training the time-series models
        :param sub_split_attrib: The attribute of the dataset whose change indicates a split in the data.
            For example: the name of the stock in a dataset with name, independent stocks"""

        self.dataset_name = dataset_name
        self.time_attrib = time_attrib
        self.sub_split_attrib = sub_split_attrib
        self._data: str = None
        self._dataframe: pd.DataFrame = None

    @property
    def data(self):
        """The raw string representing the dataset"""

        if not self._data:
            self._data = self.load_raw()
        return self._data

    @property
    def dataframe(self):
        """The pandas dataframe of the dataset"""

        if self._dataframe is None:
            self._dataframe = self.load()
        return self._dataframe

    def load(self):
        """Loads in the dataset as a dataframe

        :return: The pandas dataframe of the dataset"""

        df = pd.read_csv(io.StringIO(self.data)).astype({self.time_attrib: 'int'})
        df.sort_values(by=self.time_attrib, inplace=True)
        return df

    def sub_splits(self):
        """Split dataset into parts based off of unique values in the `self.sub_split_attrib` column

        :return: A dictionary containing the split sections of the dataset"""

        unique_grouping = self.dataframe.groupby(self.sub_split_attrib)
        return {key: unique_grouping.get_group(key) for key in unique_grouping.groups.keys() if key != self.sub_split_attrib}

    @classmethod
    def create(cls, env: str, dataset_name: str, time_attrib: str, sub_split_attrib=""):
        """Creates a handler based off of the environment name

        :param env: The environment to create the dataset for.  For example 'local' or 'ipfs'
        :param dataset_name: The name of the dataset
        :param time_attrib: The attribute of the dataset that measures the passage of time.  This is important for training the time-series models
        :param sub_split_attrib: The attribute of the dataset whose change indicates a split in the data.
            For example: the name of the stock in a dataset with name, independent stocks
        :return: An instance of the created handler"""

        for sub in cls.__subclasses__():
            if sub.__name__ == env or sub.env.lower() == env.lower():
                return sub(dataset_name, time_attrib, sub_split_attrib)

    @classmethod
    def empty(cls):
        """Creates a dummy data handler

        :return: An empty data handler"""

        return cls("", "")

    @property
    @abc.abstractmethod
    def size(self):
        """The size of the dataset"""
        ...

    @abc.abstractmethod
    def start(self, mode: int):
        """Performs any initialization operations before saving or loading

        :param mode: The mode to set the handler to"""

        raise NotImplementedError()

    @abc.abstractmethod
    def save_chunk(self, data: bytes):
        """Saves data by chunk

        :param data: The partial data to save to the dataset"""

        raise NotImplementedError()

    @abc.abstractmethod
    def save(self, data: bytes):
        """Saves all the data at once

        :param data: The data to save to the dataset"""

        raise NotImplementedError()

    @abc.abstractmethod
    def load_raw(self) -> str:
        """Loads the raw string of the dataset from the environment

        :return: The raw string representation of the dataset"""

        raise NotImplementedError()

    @abc.abstractmethod
    def finish(self):
        """Performs any finalization operations before saving or loading"""

        raise NotImplementedError()


class LocalDataHandler(DataHandler):
    """Manages the saving and usage of datasets in the local environment"""

    env = "local"

    def __init__(self, dataset_name: str, time_attrib: str, sub_split_attrib=""):
        """Manages the saving and usage of datasets in the local environment

        :param dataset_name: The name of the dataset
        :param time_attrib: The attribute of the dataset that measures the passage of time.  This is important for training the time-series models
        :param sub_split_attrib: The attribute of the dataset whose change indicates a split in the data.
            For example: the name of the stock in a dataset with name, independent stocks"""

        super().__init__(dataset_name, time_attrib, sub_split_attrib)
        self.file: io.StringIO = None
        ds_dir = f"data/{dataset_name}"
        os.makedirs(ds_dir, exist_ok=True)
        self.file_path = f"{ds_dir}/{dataset_name}.csv"
        self.mode = None
        """Locks the handler into one mode until finalization to avoid unexpected behavior"""

    @property
    def size(self):
        return os.path.getsize(self.file_path)

    def start(self, mode: int):
        self.mode = mode
        if mode == self.SAVE_MODE:
            self.file = open(self.file_path, "a")
            self.file.truncate(0)
        elif mode == self.LOAD_MODE:
            self.file = open(self.file_path, "r")

    def save_chunk(self, data: str):
        if self.mode is None:
            self.start(self.SAVE_MODE)
        elif self.mode != self.SAVE_MODE:
            raise AttributeError("Cannot perform save operation when not in save mode!")
        self.file.write(data)

    def save(self, data: str):
        if self.mode is None:
            self.start(self.SAVE_MODE)
        elif self.mode != self.SAVE_MODE:
            raise AttributeError("Cannot perform save operation when not in save mode!")
        self.file.write(data)

    def load_raw(self):
        if self.mode is None:
            self.start(self.LOAD_MODE)
        elif self.mode != self.LOAD_MODE:
            raise AttributeError("Cannot perform load operation when not in load mode!")

        return self.file.read()

    def finish(self):
        self.file.close()
        self.file = None
        self.mode = None


class IPFSDataHandler(DataHandler):
    """Manages the saving and usage of datasets in the IPFS environment"""

    env = "ipfs"

    def __init__(self, dataset_name: str, time_attrib: str, sub_split_attrib="", dataset_id: str = ""):
        """Manages the saving and usage of datasets in the local environment

        :param dataset_name: The name of the dataset
        :param time_attrib: The attribute of the dataset that measures the passage of time.  This is important for training the time-series models
        :param sub_split_attrib: The attribute of the dataset whose change indicates a split in the data.
            For example: the name of the stock in a dataset with name, independent stocks"""

        super().__init__(dataset_name, time_attrib, sub_split_attrib)
        self.file_name = dataset_name
        self.dataset_id = dataset_id
        self.proxy_handler = LocalDataHandler(dataset_name, time_attrib, sub_split_attrib)
        self.mode = None
        """Locks the handler into one mode until finalization to avoid unexpected behavior"""

    @property
    def size(self):
        return len(self.data)

    def start(self, mode: int):
        self.mode = mode
        self.proxy_handler.start(mode)

    def save_chunk(self, data: str):
        if self.mode is None:
            self.start(self.SAVE_MODE)
        elif self.mode != self.SAVE_MODE:
            raise AttributeError("Cannot perform save operation when not in save mode!")
        self.proxy_handler.save_chunk(data)

    def save(self, data: str):
        if self.mode is None:
            self.start(self.SAVE_MODE)
        elif self.mode != self.SAVE_MODE:
            raise AttributeError("Cannot perform save operation when not in save mode!")
        self.proxy_handler.save(data)

    def load_raw(self):
        if self.mode is None:
            self.start(self.LOAD_MODE)
        elif self.mode != self.LOAD_MODE:
            raise AttributeError("Cannot perform load operation when not in load mode!")

        return dataManager.web3.download(self.dataset_id)

    def finish(self):
        out = None
        if self.mode == self.SAVE_MODE:
            resp = dataManager.web3.upload_file(self.proxy_handler.file_path)
            self.proxy_handler.finish()
            out = resp["cid"]

        self.mode = None
        return out


def save_dataset(env: str, ds_name: str, ds_link: str, txn_id: str, user_id: str, time_attrib: str, endpoint="", sub_split_attrib="", **_):
    """Saves a dataset using the given data and appends an entry into the database

    :param env: The environment to create the dataset for.  For example 'local' or 'ipfs'
    :param ds_name: The name of the dataset
    :param ds_link: The URL to the data of the dataset
    :param txn_id: The id of the transaction that initiated the saving of this dataset
    :param user_id: The address of the user that is saving this dataset
    :param time_attrib: The time attribute of the dataset
    :param endpoint: The name of the endpoint that is associated with the dataset
    :param sub_split_attrib: The attribute that is used to split the dataset into independent subsets"""

    handler = DataHandler.create(env, ds_name, time_attrib, sub_split_attrib)
    size = 0
    with requests.get(ds_link, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=8192):
            size += len(chunk)
            handler.save_chunk(chunk.decode())

    handler.finish()
    dataManager.database.set("<DS>"+handler.dataset_name, {"env": handler.env, "size": size, "txn_id": txn_id, "user_id": user_id,
                                                        "time_attrib": time_attrib,"sub_split_attrib": sub_split_attrib,
                                                        "endpoint": endpoint})


def load_dataset(ds_name: str):
    """Loads dataset information from both the handler and the database

    :param ds_name: The name of the dataset to load
    :return: A handler for the dataset and the metadata associated with the dataset"""

    dataset_attribs = dataManager.database.get("<DS>" + ds_name)
    if dataset_attribs is None:
        raise Exception(f"Could not find dataset '{ds_name}'!")

    handler = LocalDataHandler(ds_name, dataset_attribs["time_attrib"],
                               sub_split_attrib=dataset_attribs.get("sub_split_attrib", ""))

    return handler, dataset_attribs