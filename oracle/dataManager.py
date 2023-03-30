import io
import web3storage
import redis
import abc
import requests
import os
from typing import Generator
import utils
from hashlib import sha256


database = redis.Redis()
web3 = web3storage.Client(utils.STORAGE_KEY)


class DataHandler:
    """Manages the saving and usage of datasets"""

    SAVE_MODE = 0
    LOAD_MODE = 1
    env = ""

    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name

    @classmethod
    def create(cls, env: str, dataset_name: str):
        """Creates a handler based off of the environment name"""
        for sub in cls.__subclasses__():
            if sub.__name__ == env or sub.env.lower() == env.lower():
                return sub(dataset_name)

    @abc.abstractmethod
    def start(self, mode: int):
        """Performs any initialization operations before saving or loading"""
        raise NotImplementedError()

    @abc.abstractmethod
    def save_chunk(self, data: bytes):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_all(self, data: bytes):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_data_loader(self, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_all(self, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def finish(self):
        """Performs any finalization operations before saving or loading"""
        raise NotImplementedError()


class LocalDataHandler(DataHandler):
    """DataLoader specifically for files stored in the local environment"""

    env = "local"

    def __init__(self, dataset_name: str):
        super().__init__(dataset_name)
        self.dataset_name = dataset_name
        self.file: io.FileIO = None
        self.file_path = f"data/{dataset_name}"
        self.mode = None
        """Locks the handler into one mode until finalization to avoid unexpected behavior"""

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

    def get_data_loader(self, **kwargs):
        """Returns a generator that generates the data in the dataset"""
        if self.mode is None:
            self.start(self.LOAD_MODE)
        elif self.mode != self.LOAD_MODE:
            raise AttributeError("Cannot perform load operation when not in load mode!")

        def gen():
            """A generator to sequentially yield all the data in the set"""
            line = self.file.readline()
            while line:
                yield line
                line = self.file.readline()
            self.file.close()

        return gen()

    def get_all(self, **kwargs):
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
    """DataLoader specifically for files stored in IPFS"""

    env = "ipfs"

    def __init__(self, dataset_name: str, dataset_id: str = ""):
        super().__init__(dataset_name)
        self.dataset_name = dataset_name
        self.file_name = dataset_name
        self.proxy_handler = LocalDataHandler(dataset_name)
        self.mode = None
        """Locks the handler into one mode until finalization to avoid unexpected behavior"""

    def start(self, mode: int):
        self.mode = mode
        self.proxy_handler.start(mode)

    def save_chunk(self, data: bytes):
        if self.mode is None:
            self.start(self.SAVE_MODE)
        elif self.mode != self.SAVE_MODE:
            raise AttributeError("Cannot perform save operation when not in save mode!")
        self.proxy_handler.save_chunk(data)

    def save_all(self, data: bytes):
        if self.mode is None:
            self.start(self.SAVE_MODE)
        elif self.mode != self.SAVE_MODE:
            raise AttributeError("Cannot perform save operation when not in save mode!")
        self.proxy_handler.save_all(data)

    def get_data_loader(self, cid: str, **kwargs):
        """Returns a generator that generates the data in the dataset"""
        if self.mode is None:
            self.start(self.LOAD_MODE)
        elif self.mode != self.LOAD_MODE:
            raise AttributeError("Cannot perform load operation when not in load mode!")

        def gen():
            """A generator to sequentially yield all the data in the set"""
            yield self.get_all(cid)

        return gen()

    def get_all(self, cid: str, **kwargs):
        if self.mode is None:
            self.start(self.LOAD_MODE)
        elif self.mode != self.LOAD_MODE:
            raise AttributeError("Cannot perform load operation when not in load mode!")

        return web3.download(cid)

    def finish(self):
        out = None
        if self.mode == self.SAVE_MODE:
            resp = web3.upload_file(self.proxy_handler.file_path)
            self.proxy_handler.finish()
            out = resp["cid"]

        self.mode = None
        return out


def save_dataset(env: str, dataset_name: str, link: str, txn_id: str, user_id: str):
    """Saves a dataset using the given data handler and appends an entry into the database"""
    handler = DataHandler.create(env, dataset_name)
    size = 0
    with requests.get(link, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=8192):
            size += len(chunk)
            handler.save_chunk(chunk)

    handler.finish()
    database.hset("<DS>"+handler.dataset_name, mapping={"env": handler.env, "size": size, "txn_id": txn_id, "user_id": user_id})


def load_dataset(dataset_name: str):
    """Loads dataset information from both the handler and the database"""
    dataset_attribs = database.hgetall("<DS>" + dataset_name)
    handler = LocalDataHandler(dataset_name)
    return handler, dataset_attribs