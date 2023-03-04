#!/usr/bin/bash

raspi-gpio set 20 op dh

[ -f /home/juice/.local/state/charging_on ] && rm /home/juice/.local/state/charging_on

