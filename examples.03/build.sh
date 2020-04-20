#!/bin/bash

#GIT_USERNAME=$1
#GIT_TOKEN=$2

#echo "GIT_USERNAME=$GIT_USERNAME"
##echo "GIT_TOKEN=$GIT_TOKEN"
echo "BOLOS_ENV=$BOLOS_ENV"
echo "BOLOS_SDK=$BOLOS_SDK"

cd /build
#git clone https://$GIT_USERNAME:$GIT_TOKEN@github.com/LedgerHQ/ledger-app-btc.git
git clone https://github.com/LedgerHQ/ledger-app-btc.git
cd ledger-app-btc
make
cp bin/* /mount

