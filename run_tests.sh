#!/bin/bash

if [ -z "$1" ]; then
  py.test -Wa -s -v trade_tariff_reference
else
  py.test -Wa -s -v "$1"
fi

