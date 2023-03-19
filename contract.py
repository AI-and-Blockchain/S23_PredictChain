from utils import *
from constants import *
import base64
from algosdk import account, mnemonic, transaction
from algosdk.atomic_transaction_composer import *
from algosdk.v2client import algod
from pyteal import *


CONTRACT_NAME = "PredictChain"
## Contract logic
count_key = Bytes("Count")

# Create an expression to store 0 in the `Count` global variable and return 1
handle_creation = Seq(App.globalPut(count_key, Int(0)), Approve())

# Main router class
router = Router(
    # Name of the contract
    CONTRACT_NAME,
    # What to do for each on-complete type when no arguments are passed (bare call)
    BareCallActions(
        # On create only, just approve
        no_op=OnCompleteAction.create_only(handle_creation),
        # Always let creator update/delete but only by the creator of this contract
        update_application=OnCompleteAction.always(Reject()),
        delete_application=OnCompleteAction.always(Reject()),
        # No local state, don't bother handling it.
        close_out=OnCompleteAction.never(),
        opt_in=OnCompleteAction.never(),
    ),
)


@router.method
def increment():
    # Declare the ScratchVar as a Python variable _outside_ the expression tree
    scratchCount = ScratchVar(TealType.uint64)
    return Seq(
        Assert(Global.group_size() == Int(1)),
        # The initial `store` for the scratch var sets the value to
        # whatever is in the `Count` global state variable
        scratchCount.store(App.globalGet(count_key)),
        # Increment the value stored in the scratch var
        # and update the global state variable
        App.globalPut(count_key, scratchCount.load() + Int(1)),
    )


@router.method
def decrement():
    # Declare the ScratchVar as a Python variable _outside_ the expression tree
    scratchCount = ScratchVar(TealType.uint64)
    return Seq(
        Assert(Global.group_size() == Int(1)),
        # The initial `store` for the scratch var sets the value to
        # whatever is in the `Count` global state variable
        scratchCount.store(App.globalGet(count_key)),
        # Check if the value would be negative by decrementing
        If(
            scratchCount.load() > Int(0),
            # If the value is > 0, decrement the value stored
            # in the scratch var and update the global state variable
            App.globalPut(count_key, scratchCount.load() - Int(1)),
        ),
    )


# helper function to compile program source
def compile_program(source_code):
    compile_response = ALGOD_CLIENT.compile(source_code)
    return base64.b64decode(compile_response["result"])


# helper function that formats global state for printing
def format_state(state):
    formatted = {}
    for item in state:
        key = item["key"]
        value = item["value"]
        formatted_key = base64.b64decode(key).decode("utf-8")
        if value["type"] == 1:
            # byte string
            if formatted_key == "voted":
                formatted_value = base64.b64decode(value["bytes"]).decode("utf-8")
            else:
                formatted_value = value["bytes"]
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value["uint"]
    return formatted


# helper function to read app global state
def read_global_state(client, app_id):
    app = client.application_info(app_id)
    global_state = (
        app["params"]["global-state"] if "global-state" in app["params"] else []
    )
    return format_state(global_state)


# create new application
def create_app(client, private_key, approval_program, clear_program, global_schema, local_schema):
    # define sender as creator
    sender = account.address_from_private_key(private_key)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        sender,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
    )

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # wait for confirmation
    try:
        transaction_response = transaction.wait_for_confirmation(client, tx_id, 5)
        print("TXID: ", tx_id)
        print(
            "Result confirmed in round: {}".format(
                transaction_response["confirmed-round"]
            )
        )

    except Exception as err:
        print(err)
        return

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id:", app_id)

    return app_id


# call application
def call_app(client, private_key, index, contract):
    # get sender address
    sender = account.address_from_private_key(private_key)
    # create a Signer object
    signer = AccountTransactionSigner(private_key)

    # get node suggested parameters
    sp = client.suggested_params()

    # Create an instance of AtomicTransactionComposer
    atc = AtomicTransactionComposer()
    atc.add_method_call(
        app_id=index,
        method=contract.get_method_by_name("increment"),
        sender=sender,
        sp=sp,
        signer=signer,
        method_args=[],  # No method args needed here
    )

    # send transaction
    results = atc.execute(client, 2)

    # wait for confirmation
    print("TXID: ", results.tx_ids[0])
    print("Result confirmed in round: {}".format(results.confirmed_round))


def main():

    # define private keys
    creator_private_key = get_private_key_from_mnemonic(creator_mnemonic)

    # declare application state storage (immutable)
    local_ints = 0
    local_bytes = 0
    global_ints = 1
    global_bytes = 0
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    # Compile the program
    approval_program, clear_program, contract = router.compile_program(version=6)

    with open("./approval.teal", "w") as f:
        f.write(approval_program)

    with open("./clear.teal", "w") as f:
        f.write(clear_program)

    with open("./contract.json", "w") as f:
        import json

        f.write(json.dumps(contract.dictify()))

    # compile program to binary
    approval_program_compiled = compile_program(approval_program)

    # compile program to binary
    clear_state_program_compiled = compile_program(clear_program)

    print("--------------------------------------------")
    print("Deploying Counter application......")

    # create new application
    app_id = create_app(
        ALGOD_CLIENT,
        creator_private_key,
        approval_program_compiled,
        clear_state_program_compiled,
        global_schema,
        local_schema,
    )

    # read global state of application
    print("Global state:", read_global_state(ALGOD_CLIENT, app_id))

    print("--------------------------------------------")
    print("Calling Counter application......")
    call_app(ALGOD_CLIENT, creator_private_key, app_id, contract)

    # read global state of application
    print("Global state:", read_global_state(ALGOD_CLIENT, app_id))


if __name__ == "__main__":
    main()
