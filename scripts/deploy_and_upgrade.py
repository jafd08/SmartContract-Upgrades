from scripts.helpful_scripts import encode_function_data, get_account, upgrade
from brownie import (
    network,
    Box,
    ProxyAdmin,
    Contract,
    TransparentUpgradeableProxy,
    BoxV2,
)


def main():
    account = get_account()
    print(f" Deplyoying to {network.show_active()} ")
    box = Box.deploy({"from": account})  # , publish_source=True

    proxy_admin = ProxyAdmin.deploy({"from": account})  # , publish_source=True

    # initializer = box.store, 1  # encode for our proxy
    box_encoded_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
        # publish_source=True,
    )  # params => logic, admin , data
    # sometimes with proxy they have hard time calculating the gas limit
    print(f" Proxy deployed to {proxy} , you can now upgrade to V2! ")
    # call function
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})

    # upgrade to V2

    box_v2 = BoxV2.deploy({"from": account})  # , publish_source=True
    upgrade_tx = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_tx.wait(1)
    print(" Proxy has been upgraded!! ")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print("proxy_box retrv :", proxy_box.retrieve())
