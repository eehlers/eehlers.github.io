#!/usr/bin/env python3

import pprint
from decimal import Decimal
from binascii import hexlify, unhexlify

from test_framework.address import byte_to_base58, program_to_witness, chars
from test_framework.messages import CTransaction, CTxIn, CTxOut, COutPoint, ToHex, COIN, sha256, CTxInWitness
from test_framework.script import (
    OP_0, OP_1, OP_2, OP_3, OP_4, OP_7,
    OP_IF, OP_ELSE, OP_ENDIF, OP_CHECKMULTISIG, OP_CHECKLOCKTIMEVERIFY,
    OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, OP_DROP,
    CScript, CScriptOp, CScriptNum,
    hash160, SIGHASH_ALL, SegwitV0SignatureHash
)
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import hex_str_to_bytes
from test_framework.key import ECKey

from hwilib import serializations

SEGWIT_OP_ZERO = b''
SEGWIT_OP_TRUE = b'\x01'

def bytes_to_hex_str(byte_str):
    return hexlify(byte_str).decode('ascii')

def base58_decode(s):
    """Decode a base58-encoding string, returning bytes"""
    if not s:
        return b''

    # Convert the string to an integer
    n = 0
    for c in s:
        n *= 58
        if c not in chars:
            raise InvalidBase58Error('Character %r is not a valid base58 character' % c)
        digit = chars.index(c)
        n += digit

    # Convert the integer to bytes
    h = '%x' % n
    if len(h) % 2:
        h = '0' + h
    res = unhexlify(h.encode('utf8'))

    # Add padding back.
    pad = 0
    for c in s[:-1]:
        if c == chars[0]: pad += 1
        else: break
    return b'\x00' * pad + res

class SignatureTests(BitcoinTestFramework):
    """ Fund the client wallet from the default wallet using sendtoaddress()
        Pay from the client wallet to the frozen wallet (PSBT/P2WSH) using sendtoaddress()
        Pay from the frozen wallet to the cold wallet using signrawtransactionwithkey()
        Pay from the cold wallet back to the client wallet using sendtoaddress()
    """

    def set_test_params(self):
        self.num_nodes = 1
        self.extra_args = [["-addresstype=bech32", "-txindex"]]

    def run_test(self):

        self.log.info(f"\n    DEBUG START")
        n0 = self.nodes[0]

        # TRANSACTION #0 - fund the client wallet from the default wallet
        rpc_default = n0.get_wallet_rpc("")
        n0.createwallet(wallet_name="wallet_client")
        rpc_client = n0.get_wallet_rpc("wallet_client")
        addr0 = rpc_client.getnewaddress()
        self.log.info(f"\n    DEBUG addr0={addr0}")

        txid0 = rpc_default.sendtoaddress(addr0, 10.0)
        n0.generate(6)
        self.sync_all()

        # dump the tx to the log
        raw_tx0 = rpc_default.getrawtransaction(txid0, True)
        s = pprint.pformat(raw_tx0)
        self.log.info(f"\n    DEBUG tx0={s}")

        # write the balances to the log
        bal0 = rpc_default.getbalance()
        self.log.info(f"\n    DEBUG balance default={bal0:f}")
        bal0 = rpc_client.getbalance()
        self.log.info(f"\n    DEBUG balance client={bal0:f}")

        # TRANSACTION #1 - pay from the client wallet to the frozen wallet
        n0.createwallet(wallet_name="wallet_frozen")
        rpc_frozen = n0.get_wallet_rpc("wallet_frozen")
        addr1 = rpc_frozen.getnewaddress()

        a1_info=rpc_frozen.getaddressinfo(addr1)
        a1_pubkey_hex=a1_info['pubkey']                 # 035bf438d73ebcb6fedbcfb3e3abffa9fa75f9538140bc64030ac29f5587d1e0e8
        a1_pubkey_bytes=hex_str_to_bytes(a1_pubkey_hex)
        a1_pubkey_hash160=hash160(a1_pubkey_bytes)
        a1_addr=byte_to_base58(a1_pubkey_hash160, 111)
        #assert a1_addr==addr1
        #self.log.info(f"\n    DEBUG addr1={addr1}")

        #a1_decode=base58_decode(addr1)
        #a1_strip=a1_decode[1:-4]
        #assert a1_strip==a1_pubkey_hash160
        #a1_hex=bytes_to_hex_str(a1_strip)
        #self.log.info(f"\n    DEBUG a1_hex={a1_hex}")

        # vault_address()
        witness_program = CScript([
            OP_IF,
                OP_1, a1_pubkey_bytes, a1_pubkey_bytes, OP_2, OP_CHECKMULTISIG,
            OP_ELSE,
                CScriptNum(500), OP_CHECKLOCKTIMEVERIFY, OP_DROP,
                OP_1, a1_pubkey_bytes, a1_pubkey_bytes, OP_2, OP_CHECKMULTISIG,
            OP_ENDIF
        ])
        witness_hash = sha256(witness_program)
        script_pubkey = CScript([OP_0, witness_hash])
        prog1 = program_to_witness(0, witness_hash)
        self.log.info(f"\n    DEBUG prog1={prog1}")

        # fund_wallet()
        txid1 = rpc_client.sendtoaddress(prog1, 9.0)
        n0.generate(6)
        self.sync_all()

        # dump the tx to the log
        raw_tx1 = rpc_client.getrawtransaction(txid1, True)
        s = pprint.pformat(raw_tx1)
        self.log.info(f"\n    DEBUG tx1={s}")

        # write the balances to the log
        bal0 = rpc_default.getbalance()
        self.log.info(f"\n    DEBUG balance default={bal0:f}")
        bal0 = rpc_client.getbalance()
        self.log.info(f"\n    DEBUG balance client={bal0:f}")
        #rpc_frozen.importaddress(prog1)
        rpc_frozen.importmulti([
            {
                 'scriptPubKey': script_pubkey.hex(),
                 'witnessscript': witness_program.hex(),
                 'internal': False,
                 'keypool': False,
                 'timestamp': 'now',
                 'watchonly': True,
            }
        ])
        bal0 = rpc_frozen.getbalance('*', 0, True)
        self.log.info(f"\n    DEBUG balance frozen={bal0:f}")

        # TRANSACTION #2 - pay from the frozen wallet to the cold wallet
        n0.createwallet(wallet_name="wallet_cold")
        rpc_cold = n0.get_wallet_rpc("wallet_cold")
        addr2 = rpc_cold.getnewaddress()
        self.log.info(f"\n    DEBUG addr2={addr2}")

        # construct_transaction()
        unspents = rpc_frozen.listunspent()
        inputs = [
            {
                "txid": u["txid"],
                "vout": u["vout"], 
            }
            for u in unspents
        ]
        outputs = [ { addr2 : Decimal(8.0) } ]
        tx2 = rpc_frozen.createpsbt(inputs, outputs)
        tx2 = rpc_frozen.utxoupdatepsbt(tx2)
        tx2a = serializations.PSBT()
        tx2a.deserialize(tx2)
        tx2a.inputs[0].witness_script = witness_program
        tx2b = tx2a.tx

        # Retrieve the private key and convert it into a "32-byte secret" that
        # can be used to initialize the ECKey object
        priv1 = rpc_frozen.dumpprivkey(addr1)
        k0 = base58_decode(priv1)
        # Remove the version byte prefix, the compression byte suffix, and the checksum
        k1 = k0[1:-5]
        # Set up the ECKey object and confirm that it matches back to the pubkey that we started with
        key = ECKey()
        key.set(k1, True)
        pubkey = key.get_pubkey().get_bytes()
        pubkey_hex = bytes_to_hex_str(pubkey)
        assert(pubkey_hex==a1_pubkey_hex)

        hashtype = SIGHASH_ALL
        value = int(9 * COIN)
        tx_hash = SegwitV0SignatureHash(witness_program, tx2b, 0, hashtype, value)
        signature = key.sign_ecdsa(tx_hash) + chr(hashtype).encode('latin-1')
        tx2b.wit.vtxinwit.append(CTxInWitness())
        tx2b.wit.vtxinwit[0].scriptWitness.stack = [SEGWIT_OP_ZERO, signature, SEGWIT_OP_TRUE, bytes(witness_program)]
        #tx2b.rehash()
        txid2 = rpc_default.sendrawtransaction(tx2b.serialize_with_witness().hex(), 0)
        n0.generate(6)
        self.sync_all()

        # dump the tx to the log
        raw_tx2 = rpc_frozen.getrawtransaction(txid2, True)
        s = pprint.pformat(raw_tx2)
        self.log.info(f"\n    DEBUG tx2={s}")

        # write the balances to the log
        bal0 = rpc_default.getbalance()
        self.log.info(f"\n    DEBUG balance default={bal0:f}")
        bal0 = rpc_client.getbalance()
        self.log.info(f"\n    DEBUG balance client={bal0:f}")
        bal0 = rpc_frozen.getbalance()
        self.log.info(f"\n    DEBUG balance frozen={bal0:f}")
        bal0 = rpc_cold.getbalance()
        self.log.info(f"\n    DEBUG balance cold={bal0:f}")

        # TRANSACTION #3 - pay from the cold wallet back to the client wallet
        addr3 = rpc_client.getnewaddress()
        self.log.info(f"\n    DEBUG addr3={addr3}")

        txid3 = rpc_cold.sendtoaddress(addr3, 7.0)
        n0.generate(6)
        self.sync_all()

        # dump the tx to the log
        raw_tx3 = rpc_cold.getrawtransaction(txid3, True)
        s = pprint.pformat(raw_tx3)
        self.log.info(f"\n    DEBUG tx3={s}")

        # write the balances to the log
        bal0 = rpc_default.getbalance()
        self.log.info(f"\n    DEBUG balance default={bal0:f}")
        bal0 = rpc_client.getbalance()
        self.log.info(f"\n    DEBUG balance client={bal0:f}")
        bal0 = rpc_frozen.getbalance()
        self.log.info(f"\n    DEBUG balance frozen={bal0:f}")
        bal0 = rpc_cold.getbalance()
        self.log.info(f"\n    DEBUG balance cold={bal0:f}")

        self.log.info(f"\n    DEBUG END")

if __name__ == '__main__':
    SignatureTests().main()

