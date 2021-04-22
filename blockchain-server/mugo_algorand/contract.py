import base64
from pyteal import *

def ApprovalProgram():

    create_contract = If(
        And(Global.group_size() == Int(1), Txn.application_args.length() == Int(6)),
        Seq([
            App.globalPut(Bytes('creator'), Txn.sender()),
            App.globalPut(Bytes('escrow'), Txn.sender()),
            App.globalPut(Bytes('count'), Int(0)),
            App.globalPut(Bytes('assetId'), Btoi(Txn.application_args[0])),
            App.globalPut(Bytes('startTimestamp'), Btoi(Txn.application_args[1])),
            App.globalPut(Bytes('endTimestamp'), Btoi(Txn.application_args[2])),
            App.globalPut(Bytes('minBid'), Btoi(Txn.application_args[3])),
            App.globalPut(Bytes('lowest'), Btoi(Txn.application_args[3])),
            App.globalPut(Bytes('amount'), Btoi(Txn.application_args[4])),
            App.globalPut(Bytes('artist'), Txn.application_args[5]),
            Return(Int(1))
        ]),
        Return(Int(0))
    )

    opt_in = Return(
        And(
            Global.group_size() == Int(1),
            Global.latest_timestamp() >= App.globalGet(Bytes('startTimestamp')),
            Global.latest_timestamp() < App.globalGet(Bytes('endTimestamp'))
        )
    )

    update_lowest_bid = If(
        And(
            Global.latest_timestamp() >= App.globalGet(Bytes('startTimestamp')),
            Global.latest_timestamp() < App.globalGet(Bytes('endTimestamp')),
            Global.group_size() == Int(1),
            Txn.sender() == App.globalGet(Bytes('creator')),
            Txn.application_args.length() == Int(2),
            Or(
                App.globalGet(Bytes('count')) < App.globalGet(Bytes('amount')),
                Btoi(Txn.application_args[1]) > App.globalGet(Bytes('lowest'))
            )
        ),
        Seq([
            App.globalPut(Bytes('lowest'), Btoi(Txn.application_args[1])),
            App.globalPut(Bytes('count'), App.globalGet(Bytes('count')) + Int(1)),
            Return(Int(1))
        ]),
        Return(Int(0))
    )

    participate = If(
        And(
            Global.latest_timestamp() >= App.globalGet(Bytes('startTimestamp')),
            Global.latest_timestamp() < App.globalGet(Bytes('endTimestamp')),
            Global.group_size() == Int(2),
            Gtxn[1].type_enum() == TxnType.Payment,
            Gtxn[1].receiver() == App.globalGet(Bytes('escrow')),
            Gtxn[1].amount() >= App.globalGet(Bytes('minBid'))
        ),
        If(
            Or(
                App.globalGet(Bytes('count')) < App.globalGet(Bytes('amount')),
                Gtxn[1].amount() > App.globalGet(Bytes('lowest'))
            ),
            Seq([
                App.localPut(Int(0), Concat(Itob(App.id()), Bytes('bid')), Gtxn[1].amount()),
                Return(Int(1))
            ]),
            Return(Int(0))
        ),
        Return(Int(0))
    )

    get_sender_bid = App.localGetEx(Int(0), App.id(), Concat(Itob(App.id()), Bytes('bid')))
    refund = If(
        And(
            Global.latest_timestamp() >= App.globalGet(Bytes('startTimestamp')),
            Global.latest_timestamp() < App.globalGet(Bytes('endTimestamp')),
            Global.group_size() == Int(2),
            App.optedIn(Int(0), App.id()),
            Gtxn[1].type_enum() == TxnType.Payment,
            Gtxn[1].sender() == App.globalGet(Bytes('escrow')),
            Gtxn[1].receiver() == Gtxn[0].sender(),
            Gtxn[1].amount() + Gtxn[1].fee() == App.globalGet(Bytes('lowest'))
        ),
        Seq([
            get_sender_bid,
            Return(
                And(
                    get_sender_bid.hasValue(),
                    Gtxn[1].amount() + Gtxn[1].fee() == get_sender_bid.value()
                )
            )
        ]),
        Return(Int(0))
    )

    complete_contract = If(
        And(
            Global.latest_timestamp() >= App.globalGet(Bytes('endTimestamp')),
            Global.group_size() == Int(3),
            Gtxn[1].type_enum() == TxnType.Payment,
            Gtxn[1].sender() == App.globalGet(Bytes('escrow')),
            Gtxn[1].receiver() == App.globalGet(Bytes('artist')),
            Gtxn[2].type_enum() == TxnType.AssetTransfer,
            Gtxn[2].sender() == App.globalGet(Bytes('artist')),
            Gtxn[2].xfer_asset() == App.globalGet(Bytes('assetId')),
            Gtxn[2].asset_receiver() == Gtxn[0].sender(),
            Gtxn[2].asset_amount() == Int(1)
        ),
        Seq([
            get_sender_bid,
            Return(
                And(
                    get_sender_bid.hasValue(),
                    Gtxn[1].amount() * Int(10) == get_sender_bid.value() * Int(9)
                )
            )
        ]),
        Return(Int(0))
    )

    leave_contract = If(
        App.optedIn(Int(0), Txn.application_id()),
        Seq([
            get_sender_bid,
            Return(
                And(
                    get_sender_bid.hasValue(),
                    Global.latest_timestamp() >= App.globalGet(Bytes('startTimestamp'))
                )
            )
        ]),
        Return(Int(0))
    )

    delete_contract = Return(
        And(
            Global.group_size() == Int(1),
            Txn.sender() == App.globalGet(Bytes('creator')),
            Global.latest_timestamp() > App.globalGet(Bytes('endTimestamp'))
        )
    )

    return Cond(
        [Int(0) == Txn.application_id(), create_contract],
        [OnComplete.OptIn == Txn.on_completion(), opt_in],
        [OnComplete.CloseOut == Txn.on_completion(), leave_contract],
        [OnComplete.DeleteApplication == Txn.on_completion(), delete_contract],
        [Txn.application_args[0] == Bytes('Bid'), participate],
        [Txn.application_args[0] == Bytes('Update'), update_lowest_bid],
        [Txn.application_args[0] == Bytes('Refund'), refund],
        [Txn.application_args[0] == Bytes('Win'), complete_contract]
    )


def ClearStateProgram():

    return Return(
        Global.latest_timestamp() > App.globalGet(Bytes('endTimestamp'))
    )


def compile_smart_contract(algod_client):
    teal_approval_program = compileTeal(ApprovalProgram(), mode=Mode.Application)
    compiled_approval_program = algod_client.compile(teal_approval_program)
    approval_program = base64.b64decode(compiled_approval_program['result'])

    teal_clear_program = compileTeal(ClearStateProgram(), mode=Mode.Application)
    compiled_clear_program = algod_client.compile(teal_clear_program)
    clear_program = base64.b64decode(compiled_clear_program['result'])

    return approval_program, clear_program
