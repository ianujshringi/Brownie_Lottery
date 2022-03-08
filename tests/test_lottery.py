from brownie import Lottery, accounts, config, network
from web3 import Web3


def test_get_entrance_fee():
    account = accounts[0]
    lottery = Lottery.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        config["networks"][network.show_active()]["inr_usd_price_feed"],
        {"from": account},
    )
    # 100inr = 1.33usd
    # in 10**8 decimals = 133000000
    # costToEnter would be approx 4.28
    # print(lottery.inrToUsd())
    entranceFee = lottery.getEntranceFee()
    print(entranceFee)
    assert entranceFee > Web3.toWei(0.00049, "ether")
    assert entranceFee < Web3.toWei(0.00053, "ether")
