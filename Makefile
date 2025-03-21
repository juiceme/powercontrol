TARBALL = powercontrol.tar.gz
INSTALL_ROOT = ./installroot
USER_DIRECTORY ?= pi
POWERCONTROL_UNIT = $(INSTALL_ROOT)/etc/systemd/system/powercontrol.service
WEBFRONT_UNIT = $(INSTALL_ROOT)/etc/systemd/system/webfront.service
POWERMEASUREMENT_UNIT = $(INSTALL_ROOT)/etc/systemd/system/powermeasurement.service
SCHEDULER_APP = /home/$(USER_DIRECTORY)/.local/bin/power_scheduler.py
WEBFRONT_APP = /home/$(USER_DIRECTORY)/.local/bin/webfront.py
POWERMEAS_APP = /home/$(USER_DIRECTORY)/.local/bin/power_measurement.py
CONFIG_FILE = /home/$(USER_DIRECTORY)/.local/state/power_config.json
CONFIG_FILE_LOCATION = $(INSTALL_ROOT)/$(CONFIG_FILE)

build: directories config_file systemd_units
	@cp ./scripts/* $(INSTALL_ROOT)/home/$(USER_DIRECTORY)/.local/bin/
	tar cfz $(TARBALL) --owner=root --group=root -C $(INSTALL_ROOT) .

directories:
	@mkdir -p $(INSTALL_ROOT)/home/$(USER_DIRECTORY)/.local/bin/
	@mkdir -p $(INSTALL_ROOT)/etc/systemd/system/multi-user.target.wants/

systemd_units:
	## install unit files
	@ln -s /etc/systemd/system/powercontrol.service $(INSTALL_ROOT)/etc/systemd/system/multi-user.target.wants/powercontrol.service
	@ln -s /etc/systemd/system/webfront.service $(INSTALL_ROOT)/etc/systemd/system/multi-user.target.wants/webfront.service
	@ln -s /etc/systemd/system/powermeasurement.service $(INSTALL_ROOT)/etc/systemd/system/multi-user.target.wants/powermeasurement.service 
	## Powercontrol unit
	@echo "[Unit]" > $(POWERCONTROL_UNIT)
	@echo "Description=Automatic powercontrol service" >> $(POWERCONTROL_UNIT)
	@echo "After=multi-user.target" >> $(POWERCONTROL_UNIT)
	@echo "" >> $(POWERCONTROL_UNIT)
	@echo "[Service]" >> $(POWERCONTROL_UNIT)
	@echo "Type=simple" >> $(POWERCONTROL_UNIT)
	@echo "Restart=always" >> $(POWERCONTROL_UNIT)
	@echo "ExecStart=/usr/bin/python3 $(SCHEDULER_APP) $(CONFIG_FILE)" >> $(POWERCONTROL_UNIT)
	@echo "" >> $(POWERCONTROL_UNIT)
	@echo "[Install]" >> $(POWERCONTROL_UNIT)
	@echo "WantedBy=multi-user.target" >> $(POWERCONTROL_UNIT)
	## Webfront unit
	@echo "[Unit]" > $(WEBFRONT_UNIT)
	@echo "Description=Automatic powercontrol web frontend" >> $(WEBFRONT_UNIT)
	@echo "After=multi-user.target" >> $(WEBFRONT_UNIT)
	@echo "" >> $(WEBFRONT_UNIT)
	@echo "[Service]" >> $(WEBFRONT_UNIT)
	@echo "Type=simple" >> $(WEBFRONT_UNIT)
	@echo "Restart=always" >> $(WEBFRONT_UNIT)
	@echo "ExecStart=/usr/bin/python3 $(WEBFRONT_APP) $(CONFIG_FILE)" >> $(WEBFRONT_UNIT)
	@echo "" >> $(WEBFRONT_UNIT)
	@echo "[Install]" >> $(WEBFRONT_UNIT)
	@echo "WantedBy=multi-user.target" >> $(WEBFRONT_UNIT)
	## Powermeasurement unit
	@echo "[Unit]" > $(POWERMEASUREMENT_UNIT)
	@echo "Description=Automatic powermeasurement service" >> $(POWERMEASUREMENT_UNIT)
	@echo "After=multi-user.target" >> $(POWERMEASUREMENT_UNIT)
	@echo "" >> $(POWERMEASUREMENT_UNIT)
	@echo "[Service]" >> $(POWERMEASUREMENT_UNIT)
	@echo "Type=simple" >> $(POWERMEASUREMENT_UNIT)
	@echo "ExecStart=/usr/bin/python3 $(POWERMEAS_APP) $(CONFIG_FILE)" >> $(POWERMEASUREMENT_UNIT)
	@echo "" >> $(POWERMEASUREMENT_UNIT)
	@echo "[Install]" >> $(POWERMEASUREMENT_UNIT)
	@echo "WantedBy=multi-user.target" >> $(POWERMEASUREMENT_UNIT)

config_file:
	@mkdir -p $(INSTALL_ROOT)/home/$(USER_DIRECTORY)/.local/state/
	@echo "{" > $(CONFIG_FILE_LOCATION)
	@echo "    \"url\": \"https://api.spot-hinta.fi/TodayAndDayForward\"," >> $(CONFIG_FILE_LOCATION)
	@echo "    \"statepath\": \"/home/$(USER_DIRECTORY)/.local/state\"," >> $(CONFIG_FILE_LOCATION)
	@echo "    \"binpath\": \"/home/$(USER_DIRECTORY)/.local/bin\"," >> $(CONFIG_FILE_LOCATION)
	@echo "    \"password\": \"change-me\"," >> $(CONFIG_FILE_LOCATION)
	@echo "    \"override\": false," >> $(CONFIG_FILE_LOCATION)
	@echo "    \"pricing\": {" >> $(CONFIG_FILE_LOCATION)
	@echo "        \"seasonal_pricing\": true," >> $(CONFIG_FILE_LOCATION)
	@echo "        \"winter_day\": 6.0," >> $(CONFIG_FILE_LOCATION)
	@echo "        \"other\": 2.0" >> $(CONFIG_FILE_LOCATION)
	@echo "    }," >> $(CONFIG_FILE_LOCATION)
	@echo "    \"limits\": {" >> $(CONFIG_FILE_LOCATION)
	@echo "        \"floor\": 12.0," >> $(CONFIG_FILE_LOCATION)
	@echo "        \"heat\": 8.0," >> $(CONFIG_FILE_LOCATION)
	@echo "        \"charging\": 6.0" >> $(CONFIG_FILE_LOCATION)
	@echo "    }," >> $(CONFIG_FILE_LOCATION)
	@echo "    \"measurements\": {" >> $(CONFIG_FILE_LOCATION)
	@echo "        \"enabled\": true," >> $(CONFIG_FILE_LOCATION)
	@echo "        \"publisher\": \"localhost\"," >> $(CONFIG_FILE_LOCATION)
	@echo "        \"topic\": \"shellypro3em-xxxxxxxxxxxx/events/rpc\"" >> $(CONFIG_FILE_LOCATION)
	@echo "    }" >> $(CONFIG_FILE_LOCATION)
	@echo "}" >> $(CONFIG_FILE_LOCATION)

clean:
	rm -rf $(TARBALL) $(INSTALL_ROOT)
