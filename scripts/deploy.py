from distutils.command.config import config
from brownie import Lottery, config, network
from scripts.script_helper import get_account, get_contract


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


def main():
    deploy_lottery()
