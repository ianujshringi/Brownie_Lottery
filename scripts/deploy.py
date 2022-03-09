from brownie import Lottery
from scripts.script_helper import get_account, get_contract


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("inr_usd_price_feed").address,
    )


def main():
    deploy_lottery()
