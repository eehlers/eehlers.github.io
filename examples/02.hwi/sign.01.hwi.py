#!/usr/bin/env python3

import os

from hwilib import commands, serializations
from hwilib.devices import ledger

PSBT_SERIALIZED = "cHNidP8BAF4CAAAAAc2uvxAMLfuPRvdrPWEPfgenmmC8sm6pzObjq41Rs+/0AAAAAAD9////AbLZ9QUAAAAAIgAgQXvPuV6U7sNpAz8QtdBpyP2lOf2vTzBq3CFEjc8pZmoAAAAAAAEBKwDh9QUAAAAAIgAgUC3XiO/a/+8xQxqsq0/s0qnOf4dzIE+P0H8c3dO8lSABBdpjUiEDJaQ8JLiKdeUJyOCuY9F037m33cq+6s4pBO2k3PxJAK4hA3viCEcdj6zxpto9KuYLiEt71I+94DWmUlK/XPbLIWOoIQOQqwYt20IjC/pNgLSdBmwCaw8F4LbaJkcNlNS4BiIej1OuZwL0AbJ1UiEDJaQ8JLiKdeUJyOCuY9F037m33cq+6s4pBO2k3PxJAK4hArAN8dXYwbgGHa2PTCDi2mKD+Uhm4Yuo0oDdz+B8WS1MIQIQOa9F75invtW6Em7jybPEzMgz9xJiNxaOoPq0qWTAhFOuaCIGAyWkPCS4inXlCcjgrmPRdN+5t93KvurOKQTtpNz8SQCuFHPF2gosAACAAAAAgAAAAAAAAAAAIgYDe+IIRx2PrPGm2j0q5guIS3vUj73gNaZSUr9c9sshY6gUC+F07iwAAIAAAACAAAAAAAAAAAAiBgOQqwYt20IjC/pNgLSdBmwCaw8F4LbaJkcNlNS4BiIejxSNVf8NLAAAgAAAAIAAAAAAAAAAAAAA"

if "LEDGER_PROXY_ADDRESS" in os.environ and "LEDGER_PROXY_PORT" in os.environ:
    client = ledger.LedgerClient("", emulator=True)
else:
    devices = commands.enumerate()
    n = len(devices)
    assert n == 1, f"{n} devices connected: only one device allowed for now"
    device = devices[0]
    client = ledger.LedgerClient(device["path"])
client.is_testnet = True
psbt = serializations.PSBT()
psbt.deserialize(PSBT_SERIALIZED)
psbt_signed = client.sign_tx(psbt)["psbt"]

