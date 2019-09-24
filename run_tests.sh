#!/bin/bash

if [ -z "$1" ]; then
  py.test -Wa -s -v --runxfail trade_tariff_reference
else
  py.test -Wa -s -v --runxfail "$1"
fi

