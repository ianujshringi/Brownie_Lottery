from re import L
from brownie import accounts, config, network, exceptions
import pytest
from scripts.deploy import deploy_lottery
from web3 import Web3
from scripts.script_helper import (
    LOCAL_BLOCKCHAIN_ENV,
    get_account,
    fund_with_link,
    get_contract,
)


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    # 1 eth =  3358.12 usd
    # 1 inr = 0.013 usd
    # 1 eth / 1 inr = 3358.12 / 0.013 usd == 1 eth = 258316.92307692 inr
    # 100 inr = 0.000387121365525900 eth
    entranceFee = lottery.getEntranceFee()
    assert entranceFee == Web3.toWei(0.000387121365525900, "ether")


def test_cant_enter_unless_start():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    # Act  Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter(
            {
                "from": get_account(),
                "value": lottery.getEntranceFee() + 100000000,
            }
        )


def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    # Assert
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    transaction.wait(1)
    requestId = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RAND = 98
    # Balace of account and adress before picking winner
    starting_balance_of_account = get_account(index=2).balance()
    balance_of_lottery = lottery.balance()
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestId, STATIC_RAND, lottery.address, {"from": account}
    ).wait(1)

    # 98 % 3 = 2
    # Assert
    assert lottery.recentWinner() == get_account(index=2)
    assert lottery.balance() == 0
    assert (
        get_account(index=2).balance()
        == starting_balance_of_account + balance_of_lottery
    )
