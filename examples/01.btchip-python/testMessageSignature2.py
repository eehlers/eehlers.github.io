#!/usr/bin/env python

import hashlib
import binascii

from btchip.btchip import *
from btchip.btchipUtils import *
from btchip import bitcoinTransaction

messageStr = "hello world"
message = bytes(messageStr, encoding='utf8')
h = hashlib.sha256()
h.update(message)
print("hash=\n" + h.hexdigest())

dongle = getDongle(True)
app = btchip(dongle)

pubkey = app.getWalletPublicKey("0/0")
print(binascii.hexlify(pubkey['publicKey']))

print("app.signMessagePrepare()")
app.signMessagePrepare("44'/0'/0'/0/0", message)
print("app.signMessageSign()")
signature = app.signMessageSign()
print("binascii.hexlify(signature)=")
print(binascii.hexlify(signature))

