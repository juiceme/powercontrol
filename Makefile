TARBALL = powercontrol.tar.gz
INSTALL_ROOT = ./installroot
USER_DIRECTORY = juice
SYSTEMD_UNIT = $(INSTALL_ROOT)/etc/systemd/system/powercontrol.service
SCHEDULER_APP = /home/$(USER_DIRECTORY)/.local/bin/power_scheduler.py
CONFIG_FILE = /home/$(USER_DIRECTORY)/.local/state/power_config.json
CONFIG_FILE_LOCATION = $(INSTALL_ROOT)/$(CONFIG_FILE)

build: config_file systemd_unit
	@cp ./scripts/* $(INSTALL_ROOT)/home/$(USER_DIRECTORY)/.local/bin/
	tar cfz $(TARBALL) --owner=root --group=root -C $(INSTALL_ROOT) .

systemd_unit:
	@mkdir -p $(INSTALL_ROOT)/etc/systemd/system/multi-user.target.wants/
	@ln -s /etc/systemd/system/powercontrol.service $(INSTALL_ROOT)/etc/systemd/system/multi-user.target.wants/powercontrol.service
	@echo "[Unit]" > $(SYSTEMD_UNIT)
	@echo "Description=Automatic powercontrol" >> $(SYSTEMD_UNIT)
	@echo "After=multi-user.target" >> $(SYSTEMD_UNIT)
	@echo "" >> $(SYSTEMD_UNIT)
	@echo "[Service]" >> $(SYSTEMD_UNIT)
	@echo "Type=simple" >> $(SYSTEMD_UNIT)
	@echo "Restart=always" >> $(SYSTEMD_UNIT)
	@echo "ExecStart=/usr/bin/python3 $(SCHEDULER_APP) $(CONFIG_FILE)" >> $(SYSTEMD_UNIT)
	@echo "" >> $(SYSTEMD_UNIT)
	@echo "[Install]" >> $(SYSTEMD_UNIT)
	@echo "WantedBy=multi-user.target" >> $(SYSTEMD_UNIT)
	@mkdir -p $(INSTALL_ROOT)/home/$(USER_DIRECTORY)/.local/bin/

config_file:
	@mkdir -p $(INSTALL_ROOT)/home/$(USER_DIRECTORY)/.local/state/
	@echo "{" > $(CONFIG_FILE_LOCATION)
	@echo "    \"url\" : \"https://api.spot-hinta.fi/TodayAndDayForward\"," >> $(CONFIG_FILE_LOCATION)
	@echo "    \"spotfile\" : \"/home/$(USER_DIRECTORY)/.local/state/spot_price.json\"," >> $(CONFIG_FILE_LOCATION)
	@echo "    \"limits\" : {" >> $(CONFIG_FILE_LOCATION)
	@echo "        \"floor\" : 10.0," >> $(CONFIG_FILE_LOCATION)
	@echo "        \"heat\" : 5.0," >> $(CONFIG_FILE_LOCATION)
	@echo "        \"charging\" : 5.0" >> $(CONFIG_FILE_LOCATION)
	@echo "    }" >> $(CONFIG_FILE_LOCATION)
	@echo "}" >> $(CONFIG_FILE_LOCATION)

clean:
	rm -rf $(TARBALL) $(INSTALL_ROOT)

