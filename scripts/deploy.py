from time import sleep
from brownie import Lottery, config, network
from scripts.script_helper import get_account, get_contract, fund_with_link


def deploy_lottery():
    account = get_account()
    print("\n------------------Deploying Lottery--------------------\n")
    Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("inr_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["keyhash"],
        config["networks"][network.show_active()]["fee"],
        {"from": account},
    )
    print("\n--------------------Lottery Deployed-------------------\n")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    fee = lottery.getEntranceFee()
    print(f"\nEntry fee : {fee} \n")
    fee += 100000000
    tx = lottery.enter({"from": account, "value": fee})
    tx.wait(1)
    print("Entered lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # 1. fund the lottery with link
    fund_with_link(lottery.address)
    # 2. End the lottery
    end_tx = lottery.endLottery({"from": account})
    end_tx.wait(1)
    # For testnet chainlink node will take some time to respond back to contract with returning randomness
    sleep(60)
    print(f"{lottery.recentWinner()} is the new Winner!")


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    tx = lottery.startLottery({"from": account})
    tx.wait(1)
    print("The lottery is started!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
