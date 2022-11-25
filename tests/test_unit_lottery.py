from brownie import Lottery, accounts, config, network, exceptions
from web3 import Web3
import pytest
from scripts.deploy import deploy_lottery
from scripts.utils import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_link,
    get_contract,
)


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #
    lottery = deploy_lottery()
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    assert entrance_fee == expected_entrance_fee

    # 0.041
    # assert lottery.getEntranceFee() > Web3.toWei(0.038, "ether")
    # assert lottery.getEntranceFee() < Web3.toWei(0.043, "ether")


def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 100000})
    #
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 100000})
    fund_link(lottery)
    lottery.endLottery({"from": account})
    #
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    bill_value = lottery.getEntranceFee() + 100000
    lottery.enter({"from": account, "value": bill_value})
    lottery.enter({"from": get_account(index=1), "value": bill_value})
    lottery.enter({"from": get_account(index=2), "value": bill_value})
    lottery.enter({"from": get_account(index=3), "value": bill_value})
    fund_link(lottery)
    tx = lottery.endLottery({"from": account})
    request_id = tx.events["RequestedRandomness"]["requestId"]
    RANDOM_NUM = 12345
    winner_index = RANDOM_NUM % 4
    winner_account = get_account(index=winner_index)
    initial_winner_account_balance = winner_account.balance()
    lottery_balance = lottery.balance()
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, RANDOM_NUM, lottery.address, {"from": account}
    )
    #
    assert lottery.lottery_state() == 1
    assert lottery.recentWinner() == winner_account
    assert lottery.balance() == 0
    assert winner_account.balance() == initial_winner_account_balance + lottery_balance
