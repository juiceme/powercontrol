# Homecontrol scripts

This repository contains homecontrol scripts that can be used to automatically switch devices on/off based on Nord Pool electricity spot prices.

## Description

The physical device is a Raspberry Pi SBC fitted with relay-control hat. The spot prices are fetched once per day and stored to a json file. The power_scheduler script executes a loop every minute where the current prices are evaluated and devices are switched based on the configured limits.

## Installation

### Requirements

    python3
    urllib
    APScheduler

### Additionally the WEB frontend requires

    pywebio
    plotly
    pandas

### Building

    make clean
    make

The default user account for installation is "pi", and the scripts and configuration will be installed under "/home/pi".local" except for the systemd unit files which are installed under "/etc/systemd/".

If installation user directory is something else than pi, the installation build package can be correctly created by

    USER_DIRECTORY=<username> make

The makefile creates a filesystem tarball powercontrol.tar.gz which can be installed directly into the target environment:

    tar -xzvf powercontrol.tar.gz -C /

## Configuration

There is one configuration file, "~/.local/state/power_config.json". The default configuration file installed is:

    {
        "url" : "https://api.spot-hinta.fi/TodayAndDayForward",   # Where the spor prices are fetched
        "statepath" : "/home/pi/.local/state",                    # Configuration, log and state files
        "binpath" : "/home/pi/.local/bin",                        # Executables and scripts
        "password": "change-me",                                  # Password for web frontend configuration
        "override": false,                                        # Use override for the lowest hour per 6h period.
        "pricing": {
            "seasonal_pricing": true,                             # If true, take into account seasonal transfer prices
            "winter_day": 6.0,                                    # Transfer price for winter day
            "other": 2.0                                          # transfer price for all other times
        },
        "limits" : {
            "floor" : 10.0,                                       # Price limit for floor heating [cents/kWh]
            "heat" : 5.0,                                         # Price limit for boiler booster [cents/kWh]
            "charging" : 5.0                                      # Price limit for EV Charger unit [cents/kWh]
        }
    }
