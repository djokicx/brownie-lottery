from webbrowser import get
from brownie import network, config, accounts, Lottery
from scripts.helper import get_account, get_contract, fund_w_link
from web3 import Web3
import time


def deploy_lottery():

    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        # get verify key, but if not there default to false
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )

    print("Deployed Lottery!")

    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]

    tx = lottery.startLottery({"from": account})
    tx.wait(1)
    print("The lottery is started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]

    tx_gf = lottery.getEntranceFee() + 1000000
    # returns the cost to enter
    tx_el = lottery.enter({"from": account, "value": tx_gf})
    tx_el.wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]

    # fund the contract with Link
    # end the lottery
    tx = fund_w_link(lottery.address)
    tx.wait(1)

    end_tx = lottery.endLottery({"from": account})
    end_tx.wait(1)
    # since end lottery calls the chainlink vrf, we have to wait some time (few blocks) for a response
    time.sleep(30)
    print(f"{lottery.recentWinner()} is the new winner")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
