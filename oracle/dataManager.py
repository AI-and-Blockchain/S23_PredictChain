import redis
import abc
import requests
import os

database = redis.Redis()
database.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
database.get("Bahamas")
database.save()


class DataHandler:

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
    def load_chunk(self, chunk_size=1024):
        raise NotImplementedError()

    @abc.abstractmethod
    def load_all(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def finish(self):
        raise NotImplementedError()


class LocalDataHandler(DataHandler):

    def __init__(self, dataset_name):
        super().__init__(dataset_name)
        self.env = "local"
        self.dataset_name = dataset_name
        self.file = None
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
        if self.mode != self.SAVE_MODE:
            raise AttributeError("Cannot perform save operation when not in save mode!")
        self.file.write(data)

    def save_all(self, data: bytes):
        if self.mode != self.SAVE_MODE:
            raise AttributeError("Cannot perform save operation when not in save mode!")
        self.file.write(data)

    def load_chunk(self, chunk_size=1024):
        if self.mode != self.LOAD_MODE:
            raise AttributeError("Cannot perform load operation when not in load mode!")
        return self.file.read(chunk_size)

    def load_all(self):
        if self.mode != self.LOAD_MODE:
            raise AttributeError("Cannot perform load operation when not in load mode!")
        return self.file.read()

    def finish(self):
        self.file.close()
        self.file = None
        self.mode = None


def save_dataset(handler: DataHandler, link: str):
    handler.start(handler.SAVE_MODE)
    size = 0
    with requests.get(link, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=8192):
            size += len(chunk)
            handler.save_chunk(chunk)

    handler.finish()
    database.set("<DS>"+handler.dataset_name, {"env": handler.env, "size": size})


def load_dataset(handler: DataHandler):
    handler.start(handler.LOAD_MODE)
    data = b''
    chunk = handler.load_chunk()
    while chunk:
        data += chunk
        chunk = handler.load_chunk()

    handler.finish()
    dataset = database.get("<DS>"+handler.dataset_name)
    return {**dataset, "data": data}
