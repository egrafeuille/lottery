from brownie import Lottery, accounts, config, network, exceptions
from web3 import Web3
import pytest
import time
from scripts.deploy import deploy_lottery
from scripts.utils import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_link,
    get_contract,
)


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #
    lottery = deploy_lottery()
    account = get_account()
    initial_account_balance = account.balance()
    lottery.startLottery({"from": account})
    bill_value = lottery.getEntranceFee() + 100000
    lottery.enter({"from": account, "value": bill_value})
    fund_link(lottery)
    tx = lottery.endLottery({"from": account})
    time.sleep(180)
    #
    assert lottery.lottery_state() == 1
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == initial_account_balance
