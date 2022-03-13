from brownie import (
    accounts,
    config,
    network,
    Contract,
    VRFCoordinatorMock,
    MockV3Aggregator,
    LinkToken,
)

LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local"]
FORKED_LOCAL_ENV = ["mainnet-fork"]


def get_account(index=None, id=None):
    """
    This function will return the account based on the given args or network status.
    """
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENV
        or network.show_active() in FORKED_LOCAL_ENV
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "inr_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """
    This function will grab the contract addresses from config file is defined,
    otherwise it will deploy the mock version of the contract and return the mock contract.

        Args:
            contract_name(string)
        Returns:
            brownie.network.contract.ProjectContract: The most recent deployed version of the contract.
    """
    contract_type = contract_to_mock[contract_name]

    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        if len(contract_type) <= 0:
            deploy_mocks()
        if contract_name == "eth_usd_price_feed":
            contract = contract_type[-2]
        else:
            contract = contract_type[-1]

    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type.name, contract_address, contract_type.abi
        )
    print(f"{contract_name} : {contract}")
    return contract


DECIMALS = 8
INITIAL_ETH_USD_VALUE = 200000000000
INITIAL_INR_USD_VALUE = 1300000


def deploy_mocks(
    decimals=DECIMALS,
    initial_eth_usd_value=INITIAL_ETH_USD_VALUE,
    initial_inr_usd_value=INITIAL_INR_USD_VALUE,
):
    """
    This funtion will deploy mock contracts.
    """
    print("\n---------------------Deploying Mocks-------------------\n")

    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_eth_usd_value, {"from": account})
    MockV3Aggregator.deploy(decimals, initial_inr_usd_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})

    print("\n---------------------Mocks Deployed--------------------\n")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=1000000000000000
):  # =0.1link
    account = account if account else get_account
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Contract Funded!")
