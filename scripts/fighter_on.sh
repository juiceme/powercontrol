#!/usr/bin/bash

raspi-gpio set 26 op dh

[ -f /home/juice/.local/state/fighter_on ] || touch /home/juice/.local/state/fighter_on


