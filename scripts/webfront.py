#!/usr/bin/python3

# -*- coding: utf-8 -*-
from pywebio import *
from pywebio.input import *
from pywebio.output import *
import plotly.express as px
import time
import json
from dateutil import parser
from datetime import datetime
import os
import sys

serverPort = 8080

if len(sys.argv) != 2:
        print("Just one argument is needed, the configuration file")
        sys.exit()

class WebServerWidget:
        config_file_name = ""
        config = {}
        prices = {}

        def __init__(self, filename):
                self.config_file_name = filename
                self.get_config()

        def get_config(self):
                config_file = open(self.config_file_name)
                self.config = json.load(config_file)
                config_file.close()

        def save_config(self):
                json_stream = json.dumps(self.config, indent=4)
                with open(self.config_file_name, "w") as outfile:
                        outfile.write(json_stream)
                        outfile.close()

        def get_prices(self):
                price_file = open(self.config["statepath"] + "/spot_prices.json")
                self.prices = json.load(price_file)
                price_file.close()

        def get_winter_day(self, now):
                price = 0
                winter_day = False
                if self.config["pricing"]["seasonal_pricing"]:
                        if now.month > 10 or now.month < 4:
                                if now.weekday() < 5:
                                        if now.hour > 6 and now.hour < 22:
                                                price = self.config["pricing"]["winter_day"]
                                                winter_day = True
                                                return price, winter_day
                price = self.config["pricing"]["other"]
                return price, winter_day

        def get_price_now(self):
                now = datetime.now()
                base_price, winter_day = self.get_winter_day(now)
                for n in self.prices:
                        dayline = parser.parse(n["DateTime"])
                        if dayline.day == now.day and dayline.hour == now.hour:
                                price = base_price + n["PriceWithTax"] * 100
                                return price, winter_day
                return 0, False

        def get_prices_from_now(self):
                prices = []
                colors = []
                now = datetime.now()
                for n in self.prices:
                        dayline = parser.parse(n["DateTime"])
                        charging = "lightslategray"
                        if (dayline.day == now.day and dayline.hour >= now.hour) or dayline.day > now.day or dayline.month > now.month:
                                base_price, winter_day = self.get_winter_day(dayline)
                                price = base_price + n["PriceWithTax"] * 100
                                if price <= self.config["limits"]["charging"]:
                                        charging = "lime"
                                prices.append({"date" : dayline,
                                               "price" : price})
                                colors.append(charging)
                return prices, colors

        def get_states(self):
                floor = "OFF"
                heat = "OFF"
                charging = "OFF"
                if os.path.exists(self.config["statepath"] + "/floor_on"):
                        floor = "ON"
                if os.path.exists(self.config["statepath"] + "/fighter_on"):
                        heat = "ON"
                if os.path.exists(self.config["statepath"] + "/charging_on"):
                        charging = "ON"
                return floor, heat, charging

        def serve(self):
                password = ""
                while (True):
                        self.get_config()
                        self.get_prices()
                        clear()
                        price, winter_day = self.get_price_now()
                        if winter_day:
                                season = "Talviaika"
                        else:
                                season = "Muu aika"
                        put_text("Hinta nyt: %.2f cent/kWh (%s)" % (price, season))
                        floor, heat, charging = self.get_states()
                        put_text("lämitys: %s" % heat)
                        put_text("lattia: %s" % floor)
                        put_text("lataus: %s" % charging)

                        prices, colormap = self.get_prices_from_now()
                        graph = px.bar(prices, x="date", y="price", title='Sylvin lataus')
                        graph.update_traces(marker_color=colormap)
                        html = graph.to_html(include_plotlyjs="require", full_html=False)
                        put_html(html)

                        level = input("Sylvin latausraja:", type=FLOAT, value=self.config["limits"]["charging"])
                        if password == "":
                                password = input("Salasana:", type=PASSWORD)
                        if password == self.config["password"]:
                                self.config["limits"]["charging"] = level
                                self.save_config()
                        else:
                                password = ""

if __name__ == "__main__":
        # initialize object and start service
        myweb = WebServerWidget(sys.argv[1]);
        start_server(myweb.serve, port=serverPort, debug=True)
