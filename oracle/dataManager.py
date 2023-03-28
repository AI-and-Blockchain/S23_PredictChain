import io

import redis
import abc
import requests
import os
from typing import Generator

database = redis.Redis()


class DataHandler:
    """Manages the saving and usage of datasets"""

    SAVE_MODE = 0
    LOAD_MODE = 1

    def __init__(self, dataset_name):
        self.dataset_name = dataset_name
        self.env = ""

    @abc.abstractmethod
    def start(self, mode: int):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_chunk(self, data: bytes):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_all(self, data: bytes):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_data_loader(self) -> Generator:
        raise NotImplementedError()

    @abc.abstractmethod
    def finish(self):
        raise NotImplementedError()


class LocalDataHandler(DataHandler):
    """DataLoader specifically for files stored in the local environment"""

    def __init__(self, dataset_name):
        super().__init__(dataset_name)
        self.env = "local"
        self.dataset_name = dataset_name
        self.file: io.FileIO = None
        self.file_path = f"data/{dataset_name}"
        self.mode = None

    def start(self, mode: int):
        self.mode = mode
        if mode == self.SAVE_MODE:
            if os.path.isfile(self.file_path):
                raise FileExistsError()
            self.file = open(self.file_path, "ab")
        elif mode == self.LOAD_MODE:
            self.file = open(self.file_path, "rb")

    def save_chunk(self, data: bytes):
        if self.mode is None:
            self.start(self.SAVE_MODE)
        elif self.mode != self.SAVE_MODE:
            raise AttributeError("Cannot perform save operation when not in save mode!")
        self.file.write(data)

    def save_all(self, data: bytes):
        if self.mode is None:
            self.start(self.SAVE_MODE)
        elif self.mode != self.SAVE_MODE:
            raise AttributeError("Cannot perform save operation when not in save mode!")
        self.file.write(data)

    def get_data_loader(self):
        if self.mode is None:
            self.start(self.LOAD_MODE)
        elif self.mode != self.LOAD_MODE:
            raise AttributeError("Cannot perform load operation when not in load mode!")

        def gen():
            line = self.file.readline()
            while line:
                yield line
                line = self.file.readline()
            self.file.close()

        return gen()

    def finish(self):
        self.file.close()
        self.file = None
        self.mode = None


def save_dataset(handler: DataHandler, link: str, txn_id: str):
    """Saves a dataset using the given data handler and appends an entry into the database"""
    size = 0
    with requests.get(link, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=8192):
            size += len(chunk)
            handler.save_chunk(chunk)

    handler.finish()
    database.set("<DS>"+handler.dataset_name, {"env": handler.env, "size": size, "txn_id": txn_id})


def load_dataset(handler: DataHandler):
    """Loads dataset information from both the handler and the database"""
    handler.start(handler.LOAD_MODE)
    loader = handler.get_data_loader()
    handler.finish()
    dataset = database.get("<DS>"+handler.dataset_name)
    return {**dataset, "data_loader": loader}
