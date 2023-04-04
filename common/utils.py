import json
import abc
import base64
import threading
import time
import datetime
from common.constants import *
from algosdk import account, mnemonic
from algosdk.transaction import PaymentTxn


def check_balance(address: str):
    """Returns the current balance of the given address"""
    account_info = ALGOD_CLIENT.account_info(address)
    return account_info.get('amount')


def transact(sender: str, sender_secret: str, receiver: str, amount: int, note: str = None):
    """Creates a transaction and sends it to the blockchain
    :return: The transaction ID"""
    params = ALGOD_CLIENT.suggested_params()
    # params.flat_fee = True
    # params.fee = 1000
    if note:
        note = note.encode()

    unsigned_txn = PaymentTxn(sender, params, receiver, amount, None, note)
    signed_txn = unsigned_txn.sign(sender_secret)
    return ALGOD_CLIENT.send_transaction(signed_txn)


def wait_for_confirmation(txn_id: str, timeout: int):
    """Wait until the transaction is confirmed or rejected, or until 'timeout'
    number of rounds have passed."""
    start_round = ALGOD_CLIENT.status()["last-round"] + 1
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = ALGOD_CLIENT.pending_transaction_info(txn_id)
        except Exception:
            return
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:
            raise Exception('pool error: {}'.format(pending_txn["pool-error"]))
        ALGOD_CLIENT.status_after_block(current_round)
        current_round += 1
    raise Exception('pending tx not found in timeout rounds, timeout value = : {}'.format(timeout))


def get_txn_confirmation(txn_id: str):
    try:
        confirmed_txn = wait_for_confirmation(txn_id, 4)
    except Exception as err:
        print(err)
        return

    return confirmed_txn


def create_account():
    """Creates an algorand wallet"""
    private_key, address = account.generate_account()
    print("Creating a new user account...")
    print("Address: {}".format(address))
    print("Secret key:", private_key)
    print("Mnemonic: {}".format(mnemonic.from_private_key(private_key)))
    return address, private_key


def search_transactions(limit=10, **kwargs):
    """Searches the blockchain for recent transactions matching some given criteria"""
    transactions = []
    next_token = ""
    has_results = True
    page = 0
    batch_size = 10 if limit > 10 else limit
    # loop using next_page to paginate until there are
    # no more transactions in the response
    while has_results and len(transactions) < limit:
        response = INDEXER_CLIENT.search_transactions(**kwargs, next_page=next_token, limit=batch_size)

        has_results = len(response["transactions"]) > 0

        if has_results:
            next_token = response["next-token"]
            transactions.extend(response["transactions"])

        page += 1

    return transactions


class TransactionMonitor:
    """Polling monitor that periodically checks the blockchain to recent transactions"""

    last_round_checked = 0
    _halt = False
    pause_duration = 10

    def __init__(self, address: str, all_time=False):
        now = datetime.datetime.now().isoformat().split("T")[0]
        self.last_round_checked = search_transactions(limit=1, start_time=now)[-1]["confirmed-round"]
        self.address = address
        self.all_time = all_time

    @abc.abstractmethod
    def process_incoming(self, txn):
        raise NotImplementedError("Subclass this monitor to handle!")

    def halt(self):
        self._halt = True

    def monitor(self):
        print("Starting monitor...")

        def inner_mon():
            while not self._halt:
                transactions = search_transactions(address=self.address, address_role="receiver",
                        min_round=self.last_round_checked if not self.all_time else None, limit=10)
                [self.process_incoming(txn) for txn in transactions]
                if len(transactions):
                    self.last_round_checked = transactions[-1]["confirmed-round"]

                time.sleep(self.pause_duration)

        thread = threading.Thread(target=inner_mon, args=())
        thread.start()


def flatten_locals(local_args: dict):
    """Takes in an attribute dict from `locals()`, inlines any kwargs and removes special keys"""
    local_args = {**local_args.copy(), **local_args.copy()["kwargs"]}
    local_args.pop("kwargs")
    local_args.pop("self")
    local_args.pop("__class__")

    return local_args