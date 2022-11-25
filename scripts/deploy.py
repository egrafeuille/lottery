from scripts.utils import get_account, get_contract, fund_link
from brownie import Lottery, network, config
import time


def deploy_lottery():
    acc = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": acc},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Lottery deployed!")
    return lottery


def start_lottery():
    acc = get_account()
    lottery = Lottery[-1]
    tx1 = lottery.startLottery({"from": acc})
    tx1.wait(1)
    print("Lottery started!")


def enter_lottery():
    acc = get_account()
    lottery = Lottery[-1]
    fee = lottery.getEntranceFee() + 1000000
    tx2 = lottery.enter({"from": acc, "value": fee})
    tx2.wait(1)
    print(f"{acc} entered to lottery")


def end_lottery():
    acc = get_account()
    lottery = Lottery[-1]
    tx3 = fund_link(lottery.address)
    tx3.wait(1)
    #
    print(f"keyhash:{lottery.keyhash()}")
    print(f"fee:{lottery.fee()}")
    #
    tx4 = lottery.endLottery({"from": acc})
    tx4.wait(1)
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the new winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
