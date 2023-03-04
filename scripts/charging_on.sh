#!/usr/bin/bash

raspi-gpio set 20 op dl

[ -f /home/juice/.local/state/charging_on ] || touch /home/juice/.local/state/charging_on

