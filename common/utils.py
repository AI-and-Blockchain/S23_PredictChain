import abc
import pytz
import threading
import time
import datetime
from common.constants import *
from algosdk import account, mnemonic
from algosdk.transaction import PaymentTxn


def check_balance(address: str):
    """Returns the current balance of the given address

    :param address: The algorand address to check the balance of
    :return: The balance of the account"""

    account_info = ALGOD_CLIENT.account_info(address)
    return account_info.get('amount')


def transact(sender: str, sender_secret: str, receiver: str, amount: int, note: str = None):
    """Creates a transaction and sends it to the blockchain

    :param sender: The address of the transaction sender
    :param sender_secret: The secret key of the sender to sign the transaction
    :param receiver: The address of the transaction recipient
    :param amount: The amount to send
    :param note: The note to send along with the transaction
    :return: The id of the transaction"""

    params = ALGOD_CLIENT.suggested_params()
    # params.flat_fee = True
    # params.fee = 1000
    if note:
        note = note.encode()

    # Debug limit to make sure testing accounts are not drained
    amount = min(amount, ALGO_AMOUNT_CAP)

    unsigned_txn = PaymentTxn(sender, params, receiver, amount, None, note)
    signed_txn = unsigned_txn.sign(sender_secret)

    return "TEST_TXN_ID"
    # return ALGOD_CLIENT.send_transaction(signed_txn)


def create_account():
    """Creates an algorand wallet

    :return: The credentials to the account"""

    private_key, address = account.generate_account()
    print("Creating a new user account...")
    print("Address: {}".format(address))
    print("Secret key:", private_key)
    print("Mnemonic: {}".format(mnemonic.from_private_key(private_key)))
    return address, private_key


def search_transactions(limit=10, **kwargs):
    """Searches the blockchain for recent transactions matching some given criteria

    :param limit: The maximum number of transactions to return"""

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

    last_round_checked = 0
    _halt = False
    PAUSE_DURATION = 10

    def __init__(self, address: str, all_time=False):
        """Polling monitor that periodically checks the blockchain to recent transactions

        :param address: The address of the user
        :param all_time: Gathers complete transaction history if ``True`` instead of just recent transactions"""

        now = datetime.datetime.now(pytz.timezone('UTC')).replace(microsecond=0)
        now = now - datetime.timedelta(minutes=2)
        now_iso = now.isoformat()
        txns = search_transactions(limit=1, start_time=now_iso)
        while len(txns) == 0:
            txns = search_transactions(limit=1, start_time=now_iso)
        self.last_round_checked = txns[-1]["confirmed-round"]
        self.address = address
        self.all_time = all_time

    @abc.abstractmethod
    def process_incoming(self, txn):
        """Execute operations based on the OP code of the incoming transaction

        :param txn: The incoming transaction"""

        raise NotImplementedError("Subclass this monitor to handle!")

    def halt(self):
        """Halts the polling of the monitor"""
        self._halt = True

    def monitor(self):
        """Starts a thread to monitor any incoming transactions to the target user address"""

        print("Starting monitor...")

        def inner_mon():
            while not self._halt:
                transactions = search_transactions(address=self.address, address_role="receiver",
                        min_round=self.last_round_checked if not self.all_time else None, limit=10)
                [self.process_incoming(txn) for txn in transactions]
                if len(transactions):
                    self.last_round_checked = transactions[-1]["confirmed-round"]

                time.sleep(self.PAUSE_DURATION)

        thread = threading.Thread(target=inner_mon, args=())
        thread.start()


def flatten_locals(local_args: dict):
    """Takes in an attribute dict from `locals()`, inlines any kwargs and removes special keys

    :param local_args: A dictionary of local variables to flatten
    :return: A flattened dictionary of the attributes"""

    local_args = {**local_args.copy(), **local_args.copy().get("kwargs", {})}
    for key in ["kwargs", "self", "__class__"]:
        if key in local_args:
            local_args.pop(key)

    return local_args
