from brownie import Lottery, accounts, config, network, exceptions
from web3 import Web3
from scripts.deploy_lottery import deploy_lottery
from scripts.helper import LOCAL_CHAIN_ENV, get_account, fund_w_link, get_contract
import pytest


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_CHAIN_ENV:
        pytest.skip()
    # first we need to get an account
    # must deploy contract
    account = accounts[0]
    lottery = deploy_lottery()
    entrance_fee = lottery.getEntranceFee()
    expected_fee = Web3.toWei(0.025, "ether")
    print(f"Fee is:{entrance_fee}")
    assert entrance_fee == entrance_fee


def test_cant_enter_unless_start():
    if network.show_active() not in LOCAL_CHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_CHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_CHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_w_link(lottery.address)
    lottery.endLottery({"from": account})
    assert lottery.lotteryState() == 2


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_CHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()

    lottery.startLottery({"from": account})

    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})

    fund_w_link(lottery.address)

    starting_balance = account.balance()
    lottery_balance = lottery.balance()
    tx = lottery.endLottery({"from": account})
    request_id = tx.events["RequestedRandomness"]["requestId"]

    vrf = get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, 9, lottery.address, {"from": account}
    )

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert lottery.lotteryState() == 1
    assert account.balance() == starting_balance + lottery_balance
