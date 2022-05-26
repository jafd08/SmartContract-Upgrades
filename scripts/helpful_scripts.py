from brownie import accounts, network, config
from web3 import Web3
import eth_utils

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache", "mainnet-fork"]
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])


# initializer = box.store, 1
def encode_function_data(initializer=None, *args):
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.
        args (Any, optional):
        The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
    if not len(args):
        args = b""

    if initializer:
        return initializer.encode_input(*args)

    return b""


def upgrade(
    account,
    proxy,
    new_implementation_address,
    proxy_admin_contract=None,  # from the ProxyAdmin.sol contract
    initializer=None,
    *args
):
    transaction = None
    # args param = will be a list of X quantity of arguments received at the end
    if proxy_admin_contract:
        if initializer:
            encoded_funct_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                new_implementation_address,
                encode_function_data,
                {"from": account},
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address, new_implementation_address, {"from": account}
            )
    if initializer:
        encoded_funct_call = encode_function_data(initializer, *args)
        transaction = proxy.upgradeToAndCall(
            new_implementation_address, encoded_funct_call, {"from": account}
        )
    else:
        print(" no initializer !! ")
        transaction = proxy.upgradeTo(new_implementation_address, {"from": account})
    print("transaction :", transaction)
    return transaction
