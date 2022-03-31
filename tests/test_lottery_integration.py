# This script will be responsible for the integration test for the lottery application.

from brownie import network
import pytest
from scripts.script_helper import LOCAL_BLOCKCHAIN_ENV, get_account, fund_with_link
from scripts.deploy import deploy_lottery
from time import sleep


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
