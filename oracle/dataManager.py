import web3storage
import redis
import json
from common import utils


class Database:
    """Class used to store oracle information and provide compatability when redis is not available"""

    def __init__(self, use_redis=True):
        """Class used to store oracle information and provide compatability when redis is not available

        :param use_redis: Flag that determines if the usage of redis should be attempted"""

        self._using_redis = False
        self._dict: dict[str, dict] = {}
        if use_redis:
            # Try to use redis, default to a dictionary if there is an error
            try:
                self._redis = redis.Redis(decode_responses=True)
                self._redis.keys()
                self._using_redis = True
            except Exception:
                print("Error loading Redis! (Is it installed and running?)\nContinuing using compatability mode...")

    def set(self, key: str, value: dict):
        """Sets a key, value pair in the database

        :param key: The key to store
        :param value: The value to store"""

        if self._using_redis:
            value = json.dumps(value)
            self._redis.set(key, value)
        else:
            self._dict[key] = value

    def get(self, key: str) -> dict:
        """Gets the value of a key in the database

        :param key: The key to retrieve the value of
        :return: The value of the key"""

        if self._using_redis:
            value = self._redis.get(key)
            if value is None:
                return value
            return json.loads(value)
        return self._dict.get(key)

    def scan_iter(self, prefix=None):
        """Returns an iterator that iterates over the keys in the database

        :param prefix: Filters out all keys that do not begin with this value
        :return: An iterator over all the keys"""

        if self._using_redis:
            return self._redis.scan_iter(prefix)
        return (key for key in self._dict if prefix is None or key.startswith(prefix))

    def exists(self, key: str):
        """Checks if a key exists in the database

        :param key: The key to check for
        :return: 1 if the key is in the database, 0 otherwise"""

        if self._using_redis:
            return self._redis.exists(key)
        return 1 if key in self._dict else 0

    def keys(self):
        """Returns a list of all keys in the database

        :return: The list of database keys"""

        if self._using_redis:
            return self._redis.keys()
        return [key for key in self._dict]


database = Database()
"""Database used to store oracle information"""


web3 = web3storage.Client(utils.STORAGE_KEY)
"""The storage client for IPFS"""


def enum_database(env: str, prefix: str):
    """Enumerates the given database, filtering keys by the given prefix

    :param env: The environment to look for the data in
    :param prefix: The common prefix between all the entry keys that will be enumerated
    :return: A dictionary of all the selected keys"""

    datasets = {}

    if env == "local":
        for key in database.scan_iter(f"{prefix}*"):
            datasets[key] = database.get(key)
    else:
        raise NotImplementedError(f"Environment {env} has not been implemented!")

    return datasets


def load_database(filepath: str, overwrite=False):
    """Loads the contents of a json file and puts each item into the database

    :param filepath: The path to the file to be loaded
    :param overwrite: Flag to determine if an existing key will be overwritten by an incoming value"""

    with open(filepath, "r") as file:
        loaded = json.loads(file.read())

    for key in loaded:
        if not overwrite and database.exists(key):
            continue

        database.set(key, loaded[key])


def save_database(filepath: str):
    """Saves the contents of the database to a file

    :param filepath: The file to save the database to"""

    saved = {}

    for key in database.scan_iter():
        saved[key] = database.get(key)

    with open(filepath, "w") as file:
        file.write(json.dumps(saved))

