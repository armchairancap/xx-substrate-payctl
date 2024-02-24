# xx Network Validator Pay Control

payctl is a simple Python-based CLI utility that manages the payouts for xx Network validators.

This repository is an xx Network-specific fork of [substrate-payctl](https://github.com/stakelink/substrate-payctl), so don't install the both in the same Python environment.

There's no "analytics" or any garbage like that. Feel free to inspect the code.

## About 

[xx Network](https://xx.network) is quantum-resistant and privacy-focused blockchain ecosystem. Its blockchain is based on Substrate.

[Substrate](https://substrate.dev/) is a modular framework that enables the creation of new blockchains by composing custom pre-build components, and it is the foundation on which some of the most important recent blockchains, such as [Polkadot](https://polkadot.network/) and [xx Network](https://xx.network/), are built.

Substrate provides a [Staking](https://paritytech.github.io/substrate/master/pallet_staking/index.html) module that enables network protection through a NPoS (Nominated Proof-of-Stake) algorithm, where validators and nominators may stake funds as a guarantee to protect the network and in return they receive a reward.

The payment of the reward to validators and nominators is not automatic, and must be triggered by activating the function **payout_stakers**. It can be done using a browser and the official [xx Wallet](https://wallet.xx.network/), but this tool provides an alternative way to do it from the command line, which in turn facilitates the automation of recurring payments.

## Install

To install, find a Linux system with Python 3 that can connect to xx Network chain service using WebSocket.

Clone the repository and install the package:

```sh
python3 -m pip install substrate-interface==1.7.4
# install other modules if necessary
git clone http://github.com/armchairancap/xx-substrate-payctl
# inspect contents if you'd like but do NOT enter the subdirectory
python3 -m pip install xx-substrate-payctl/
```

## Usage

After installing the package the _payctl_ executable should be available on the system.

Common workflow:

- Go to https://wallet.xx.network and create a new account for signing (payouts). Fund it with 5 xx for transaction fees.
- Edit the configuration file you plan to use: specify your paying (Signing) account, and validating account(s) for which you want to make payouts. Change xx chain service endpoint if it's not on localhost.

```sh
mkdir $HOME/.config/payctl
nano $HOME/.config/payctl/default.conf
chmod 0600 $HOME/.config/payctl/default.conf
```

- Run `payctl pay -d 2` to pay any rewards from past 2 eras. 

Additional examples can be found further below.

```sh
$ payctl -h
usage: payctl [-h] [-c CONFIG] [-r RPC_URL] [-n NETWORK] [-d DEPTHERAS] {list,pay} ...

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        read config from a file. Example: .config/payctl/default.conf
  -r RPC_URL, --rpcurl RPC_URL
                        substrate RPC URL. Example: ws://2.2.2.2:63007
  -n NETWORK, --network NETWORK
                        name of the network to connect. Hard-coded to xx Network
  -d DEPTHERAS, --deptheras DEPTHERAS
                        depth of eras to include

Commands:
  {list,pay}            get help with: list -h and pay -h
    list                list rewards
    pay                 pay rewards

```

Since the default config path is `.config/payctl/default.conf`, you don't have to provide it if executing from $HOME. Otherwise provide `-c CONFIG`.

### Configuration 

default.conf contains default parameters. `RPCURL` tells the tools how to connect to xx chain. The value of `Network` shouldn't be changed, and the rest is up to you.

Here, Signing Account is `6aK...` - it is used to create and broadcast payout transactions and pays transaction fees. Signing Mnemonic is one of several ways to access that account's wallet. That's followed by at least one validator wallet for which to pay out unclaimed rewards (`6Vm...`, `6YLR...`):

```raw
# $HOME/.config/payctl/default.conf
[Defaults]
RPCURL = ws://127.0.0.1:63007
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
                  [validator [validator ...]]

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

These examples assume there's a valid default configuration file.

List rewards for default validators (NOTE: execution may take 5-10 seconds per each era and validator address):

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
$ payctl list 6YLRyPaxP9ugZYmLpnhmoYrZT3VLEz3JTQrjbg6wVJpspYFu 6YLRyPaxP9ugZYmLpnhmoYrZT3VLEz3JTQrjbg6wVJpspYFu
Era: 507
  6YLRyPaxP9ugZYmLpnhmoYrZT3VLEz3JTQrjbg6wVJpspYFu => 40.643866310648 xx (claimed)
```

List **only pending** rewards for a specific validator:

```sh
$ payctl list 6YLRyPaxP9ugZYmLpnhmoYrZT3VLEz3JTQrjbg6wVJpspYFu --unclaimed
Era: 507
  6YLRyPaxP9ugZYmLpnhmoYrZT3VLEz3JTQrjbg6wVJpspYFu => 40.971542087938 xx (unclaimed)
```

Pay rewards for the default validators (specified in your default.conf):

```sh
payctl pay
```

Each payment may cost around 0.01 xx per each validator account payout, so 5 xx should be able to fund hundreds of payouts for a single validator account.

Pay rewards for the default validators (from the config file) only if there are more than 2 eras pending:

```sh
payctl pay -m 2
```

## Finding transactions in xx Network Explorer

If a payout is successful, an extrinsic hash appears in the output, as well as a link to the official xx Network explorer.

Click on the link or copy the extrinsics hash and go to https://explorer.xx.network to view transaction details.
