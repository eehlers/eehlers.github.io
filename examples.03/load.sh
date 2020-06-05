#!/bin/bash

ICON=010000000000ffffffffffffffffffbffe0ffc9ff99ff91ff89ff19ff39ff10ff8bffeffffffffffff

source repos/venv/bin/activate

python -m ledgerblue.loadApp --curve secp256k1 --tlv --targetId 0x31100004 --targetVersion="1.6.0" --delete --fileName mount/app.hex --appName "Bitcoin" --appVersion 1.3.18 --dataSize 64 --icon $ICON --path "" --appFlags 0xa50 --appFlags 0xa50 --targetVersion 1.6.0

