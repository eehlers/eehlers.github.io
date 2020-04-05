#!/usr/bin/env python3

import hashlib
import os

from hwilib import commands, serializations
from hwilib.devices import ledger

messageStr = "hello world"
message = bytes(messageStr, encoding='utf8')
h = hashlib.sha256()
h.update(message)
print("hash=\n" + h.hexdigest())

if "LEDGER_PROXY_ADDRESS" in os.environ and "LEDGER_PROXY_PORT" in os.environ:
    client = ledger.LedgerClient("", emulator=True)
else:
    devices = commands.enumerate()
    n = len(devices)
    assert n == 1, f"{n} devices connected: only one device allowed for now"
    device = devices[0]
    client = ledger.LedgerClient(device["path"])
client.is_testnet = True
sig = client.sign_message(messageStr, "m/44'/0'/0'/0/0")
print(sig)

