# xx Network Validator Pay Control

Simple shell utility that manages the payouts for xx Network.

This repository is an xx Network-specific fork of [substrate-payctl](https://github.com/stakelink/substrate-payctl), so don't install both on the same system.

## About 

[xx Network](https://xx.network) is quantum-resistant and privacy-focused blockchain ecosystem. Its blockchain is based on Substrate.

[Substrate](https://substrate.dev/) is a modular framework that enables the creation of new blockchains by composing custom pre-build components, and it is the foundation on which some of the most important recent blockchains, such as [Polkadot](https://polkadot.network/) and [xx Network](https://xx.network/), are built.

Substrate provides a [Staking](https://paritytech.github.io/substrate/master/pallet_staking/index.html) module that enables network protection through a NPoS (Nominated Proof-of-Stake) algorithm, where validators and nominators may stake funds as a guarantee to protect the network and in return they receive a reward.

The payment of the reward to validators and nominators is not automatic, and must be triggered by activating the function **payout_stakers**. It can be done using a browser and the official [xx Wallet](https://wallet.xx.network/), but this tool provides an alternative way to do it from the command line, which in turn facilitates the automation of recurring payments.

## Install

To install, find a Linux system with Python 3 that can connect to xx Network chain service using WebSocket.

Clone the repository and install the package:

```sh
$ python3 -m pip install substrate-interface
$ # install other modules if necessary
$ git clone http://github.com/armchairancap/xx-substrate-payctl
$ pip install xx-substrate-payctl/
```

## Usage

After installing the package the _payctl_ executable should be available on the system.

Common workflow:

- Go to https://wallet.xx.network and create a new account for signing (payouts). Fund it with 5 xx for transaction fees.
- Edit the configuration file you plan to use: specify your paying (Signing) account, and validating account(s) for which you want to make payouts. Change xx chain service endpoint if it's not on localhost.
- Run `payctl pay` (example commands can be found in Examples, further below) to list or pay out rewards

default.conf will likely be copied to `$HOME/.local/etc/payctl/default.conf` or `/usr/local/etc/payctl/default.conf` depending on how the tool was installed, but you can use your own configuration file (e.g. `-c $HOME/my.conf`).

```
$ payctl
usage: payctl [-h] [-c CONFIG] [-n NETWORK] [-r RPCURL] [-d DEPTHERAS]
              {list,pay} ...

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        specify config file
  -n NETWORK, --network NETWORK
  -r RPCURL, --rpc-url RPCURL
  -d DEPTHERAS, --depth-eras DEPTHERAS

subcommands:
  {list,pay}
    list
    pay
```

### Configuration 

default.conf contains default parameters. `RPCURL` tells the tools how to connect to xx chain. The value of `Network` shouldn't be changed, and the rest is up to you.

Here, Signing Account is `6aK...` - it is used to create and broadcast payout transactions and pays transaction fees. Signing Mnemonic is one of several ways to access that account's wallet. That's followed by at least one validator wallet for which to pay out unclaimed rewards (`6Vm...`, `6YLR...`):

```raw
[Defaults]
RPCURL = ws://127.0.0.1:63007/
Network = xx network
DepthEras = 7
MinEras = 1
SigningAccount= 6aKtCtxiu6x6LJ1LWhL1PfnysTyR7LNzvYwAYKWFcyFKmtiK
SigningMnemonic= drip option mansion final void breeze govern fringe layer like exchange hat spy dentist miss element divorce jelly finger check exclude whiskey tango foxtrot

[6VmTDzGmk6phAUFi5FXvi5jsV3Ljm1cYAxPUJZGMYVSX1d8Q]
[6YLRyPaxP9ugZYmLpnhmoYrZT3VLEz3JTQrjbg6wVJpspYFu]
```

The payment command requires to sign the extrinsic. _SigningAccount_ is used to specify the account used for the signature, while the secret to generate the key could be specified in tree ways; _SigningMnemonic_, _SigningSeed_ or _SigningUri_. 

1. Signing information must be secret. Be careful to not expose the configuration file if it contains signing information.
2. Use a Signing Account with a small balance to sign petitions in order to minimize the impact of secret's leak. Do not use a validator account.
3. Do not use validator (cMix) system's xx chain service to lower the risk of node takeover. If you can't have a dedicated xx chain instance for payouts, use Gateway's xx chain service.

If you don't want to store SigningMnemonic in a configuration file, that and other information can also be provided at run-time:

```sh
$ payctl pay --help
usage: payctl pay [-h] [-m MINERAS] [-a SIGNINGACCOUNT] [-n SIGNINGMNEMONIC]
                  [-s SIGNINGSEED] [-u SIGNINGURI]
                  [validators [validators ...]]

positional arguments:
  validators            specify validator

optional arguments:
  -h, --help            show this help message and exit
  -m MINERAS, --min-eras MINERAS
  -a SIGNINGACCOUNT, --signing-account SIGNINGACCOUNT
  -n SIGNINGMNEMONIC, --signing-mnemonic SIGNINGMNEMONIC
  -s SIGNINGSEED, --signing-seed SIGNINGSEED
  -u SIGNINGURI, --signing-uri SIGNINGURI
```

### Examples

List rewards for default validators (NOTE: execution may take 5-10 seconds per each era and address):

```sh
$ payctl list
Era: 506
  6VmTDzGmk6phAUFi5FXvi5jsV3Ljm1cYAxPUJZGMYVSX1d8Q => 51.321933155324 xx (claimed)
  6YLRyPaxP9ugZYmLpnhmoYrZT3VLEz3JTQrjbg6wVJpspYFu => 45.123123123123 xx (claimed)
Era: 507
  6VmTDzGmk6phAUFi5FXvi5jsV3Ljm1cYAxPUJZGMYVSX1d8Q => 38.646077588588 xx (claimed)
  6YLRyPaxP9ugZYmLpnhmoYrZT3VLEz3JTQrjbg6wVJpspYFu => 39.883932892833 xx (claimed)
...
```

List rewards for default validators including the last 1 eras:

```sh
$ payctl -d 1 list
Era: 507
  6VmTDzGmk6phAUFi5FXvi5jsV3Ljm1cYAxPUJZGMYVSX1d8Q => 20.636226339558 xx (claimed)
  6YLRyPaxP9ugZYmLpnhmoYrZT3VLEz3JTQrjbg6wVJpspYFu => 35.123123123123 xx (unclaimed)
```

List rewards for a specific validator:

```sh
$ payctl list 6YLRyPaxP9ugZYmLpnhmoYrZT3VLEz3JTQrjbg6wVJpspYFu
Era: 507
  6YLRyPaxP9ugZYmLpnhmoYrZT3VLEz3JTQrjbg6wVJpspYFu => 40.643866310648 xx (claimed)
```

List **only pending** rewards for a specific validator:

```sh
$ payctl list 6YLRyPaxP9ugZYmLpnhmoYrZT3VLEz3JTQrjbg6wVJpspYFu --unclaimed
Era: 507
  6YLRyPaxP9ugZYmLpnhmoYrZT3VLEz3JTQrjbg6wVJpspYFu => 40.971542087938 xx (unclaimed)
```

Pay rewards for the default validators (from default.conf):

```sh
payctl pay
```

Each payment may cost around 0.01 xx per each validator account payout, so 5 xx should be able to fund hundreds of payouts for a single validator account.

Pay rewards for the default validators (from the config file) only if there are more than 2 eras pending:

```sh
payctl pay -m 2
```

## Finding transactions in xx Network Explorer

If a payout is successful, an extrinsic hash appears in the output.

Copy that hash, go to https://explorer.xx.network and search for the hash to find transaction details.
