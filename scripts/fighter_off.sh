#!/usr/bin/bash

raspi-gpio set 26 op dl

[ -f /home/juice/.local/state/fighter_on ] && rm /home/juice/.local/state/fighter_on

