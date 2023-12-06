from argparse import ArgumentParser
from configparser import ConfigParser
from collections import OrderedDict
from substrateinterface import SubstrateInterface
from .utils import *
from time import sleep

#
# cmd_list - 'list' subcommand handler.
#
def cmd_list(args, config):
    substrate = SubstrateInterface(url="ws://127.0.0.1:63007",ss58_format=55,use_remote_preset=True)
    active_era = substrate.query(
        module='Staking',
        storage_function='ActiveEra'
    )

    count = 1
    err = None
    while count <= 3:
        try:
            active_era = substrate.query(module='Staking', storage_function='ActiveEra')
            active_era = active_era.value['index']
            break
        except Exception as e:
            err = e
            print("Error ocurred, will retry:", err)
            if count == 3:
                raise
            count += 1
  
    depth = get_config(args, config, 'deptheras')
    depth = int(depth) if depth is not None else 84

    start = active_era - depth
    end = active_era

    eras_payment_info = get_eras_payment_info_filtered(
        substrate, start, end,
        accounts=get_included_accounts(args, config),
        only_unclaimed=args.only_unclaimed
    )
    eras_payment_info = OrderedDict(sorted(eras_payment_info.items(), reverse=True))

    for era_index, era in eras_payment_info.items():
        print(f"Era: {era_index}")
        for accountId in era:
            msg = "claimed" if era[accountId]['claimed'] else "unclaimed"
            formatted_amount = format_balance_to_symbol(substrate, era[accountId]['amount'], substrate.token_decimals)

            print(f"\t {accountId} => {formatted_amount} ({msg})")


#
# cmd_pay - 'pay' subcommand handler.
#
def cmd_pay(args, config):
    substrate = SubstrateInterface(url="ws://127.0.0.1:63007",ss58_format=55,use_remote_preset=True)

    count = 1
    err = None
    while count <= 5:
        try:
            active_era = substrate.query(module='Staking', storage_function='ActiveEra')
            active_era = active_era.value['index']
            break
        except Exception as e:
            err = e
            print("Error ocurred, will retry:", err)
            if count == 5:
                raise
            count += 1

    depth = get_config(args, config, 'deptheras')
    depth = int(depth) if depth is not None else 84

    minEras = get_config(args, config, 'mineras')
    minEras = int(minEras) if minEras is not None else 5

    start = active_era - depth
    end = active_era

    eras_payment_info = get_eras_payment_info_filtered(
        substrate, start, end,
        accounts=get_included_accounts(args, config),
        only_unclaimed=True
    )
    eras_payment_info = OrderedDict(sorted(eras_payment_info.items(), reverse=True))

    if len(eras_payment_info.keys()) == 0:
        print(f"There are no rewards to claim in the last {depth} era(s)")
        return

    if len(eras_payment_info.keys()) < minEras:
        print(
            f"There are rewards to claim on {len(eras_payment_info.keys())} era(s), " + 
            f"but those are not enough to reach the minimum threshold ({minEras})"
        )
        return

    keypair = get_keypair(args, config)

    payout_calls = []
    for era in eras_payment_info:
        for accountId in eras_payment_info[era]:
            payout_calls.append({
                'call_module': 'Staking',
                'call_function': 'payout_stakers',
                'call_args': {
                    'validator_stash': accountId,
                    'era': era,
                }                
            })

    call = substrate.compose_call(
        call_module='Utility',
        call_function='batch',
        call_params={
            'calls': payout_calls
        }
    )

    payment_info = substrate.get_payment_info(call=call, keypair=keypair)
    account_info = get_account_info(substrate, get_config(args, config, 'signingaccount'))

    expected_fees = payment_info['partialFee']
    free_balance = account_info['data']['free']
    existential_deposit = get_existential_deposit(substrate)

    if (free_balance - expected_fees) < existential_deposit:
        print(f"Account with not enough funds. Needed {existential_deposit + expected_fees}, but got {free_balance}")
        return

    signature_payload = substrate.generate_signature_payload(
        call=call,
        nonce=account_info['nonce']
    )
    signature = keypair.sign(signature_payload)

    extrinsic = substrate.create_signed_extrinsic(
        call=call,
        keypair=keypair,
        nonce=account_info['nonce'],
        signature=signature
    )

    print(
        "Submitting batch extrinsic to claim " + 
        f"{len(payout_calls)} rewards (in {len(eras_payment_info)} eras)"
    )

    extrinsic_receipt = substrate.submit_extrinsic(
        extrinsic=extrinsic,
        wait_for_inclusion=True
    )

    fees = extrinsic_receipt.total_fee_amount

    print(f"\t Extrinsic hash: {extrinsic_receipt.extrinsic_hash}")
    print("\t Extrinsics link: https://explorer.xx.network/extrinsics/" + extrinsic_receipt.extrinsic_hash)
    print(f"\t Block hash: {extrinsic_receipt.block_hash}")
    print(f"\t Total rewards released: {format_balance_to_symbol(substrate, fees)} ({fees})") # it's not "fees", it's really "rewards"
    print("\t Transaction fee:", (expected_fees/10**9),"xx")
    
    print(f"\t Status: {'ok' if extrinsic_receipt.is_success else 'error'}")
    if not extrinsic_receipt.is_success:
        print(f"\t Error message: {extrinsic_receipt.error_message.get('docs')}")

def main():
    args_parser = ArgumentParser(prog='payctl')
    args_parser.add_argument("-c", "--config", help="read config from a file", default=".config/payctl/default.conf")
    args_parser.add_argument("-r", "--rpc-url", dest="rpcurl", help="substrate RPC Url")
    args_parser.add_argument("-d", "--depth-eras", dest="deptheras", help="depth of eras to include")

    args_subparsers = args_parser.add_subparsers(title="Commands", help='', dest="command")

    args_subparser_list = args_subparsers.add_parser("list", help="list rewards")
    args_subparser_list.add_argument("-u", "--unclaimed", dest="only_unclaimed", help='show unclaimed only', action='store_true', default=False)
    args_subparser_list.add_argument("validators", nargs='*', help="", default=None)
    
    args_subparser_pay = args_subparsers.add_parser('pay', help="pay rewards")
    args_subparser_pay.add_argument("validators", nargs='*', help="", default=None)
    args_subparser_pay.add_argument("-m", "--min-eras", dest="mineras", help="minum eras pending to pay to proceed payment")
    args_subparser_pay.add_argument("-a", "--signing-account", dest="signingaccount", help="account used to sign requests")
    args_subparser_pay.add_argument("-n", "--signing-mnemonic", dest="signingmnemonic", help="mnemonic to generate the signing key")
    args_subparser_pay.add_argument("-s", "--signing-seed", dest="signingseed", help="seed to generate the signing key")
    args_subparser_pay.add_argument("-u", "--signing-uri", dest="signinguri", help="uri to generate the signing key")

    args = args_parser.parse_args()

    try:
        config = ConfigParser()
        config.read_file(open(args.config))
    except Exception as exc:
        print(f"Unable to read config: {str(exc)}")
        exit(0)

    if not args.command:
        args_parser.print_help()
        exit(1)

    if args.command == 'list':
        cmd_list(args, config)
    if args.command == 'pay':
        cmd_pay(args, config)


if __name__ == '__main__':
    main()
