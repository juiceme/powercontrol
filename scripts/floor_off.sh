#!/usr/bin/bash

[ -f /home/juice/.local/state/floor_on ] || exit 0

raspi-gpio set 21 op dl
sleep 1
raspi-gpio set 21 op dh

rm /home/juice/.local/state/floor_on

