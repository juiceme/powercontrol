TARBALL = powercontrol.tar.gz
INSTALL_ROOT = ./installroot
USER_DIRECTORY = juice
SYSTEMD_UNIT = $(INSTALL_ROOT)/etc/systemd/system/powercontrol.service

build:
	@mkdir -p $(INSTALL_ROOT)/etc/systemd/system/multi-user.target.wants/
	@ln -s /etc/systemd/system/powercontrol.service $(INSTALL_ROOT)/etc/systemd/system/multi-user.target.wants/powercontrol.service
	@echo "[Unit]" > $(SYSTEMD_UNIT)
	@echo "Description=Automatic powercontrol" >> $(SYSTEMD_UNIT)
	@echo "After=multi-user.target" >> $(SYSTEMD_UNIT)
	@echo "" >> $(SYSTEMD_UNIT)
	@echo "[Service]" >> $(SYSTEMD_UNIT)
	@echo "Type=simple" >> $(SYSTEMD_UNIT)
	@echo "Restart=always" >> $(SYSTEMD_UNIT)
	@echo "ExecStart=/usr/bin/python3 /home/$(USER_DIRECTORY)/.local/bin/power_scheduler.py" >> $(SYSTEMD_UNIT)
	@echo "" >> $(SYSTEMD_UNIT)
	@echo "[Install]" >> $(SYSTEMD_UNIT)
	@echo "WantedBy=multi-user.target" >> $(SYSTEMD_UNIT)
	@mkdir -p $(INSTALL_ROOT)/home/$(USER_DIRECTORY)/.local/bin/
	@mkdir -p $(INSTALL_ROOT)/home/$(USER_DIRECTORY)/.local/state/
	@cp ./scripts/* $(INSTALL_ROOT)/home/$(USER_DIRECTORY)/.local/bin/
	tar cfz $(TARBALL) --owner=root --group=root -C $(INSTALL_ROOT) .

clean:
	rm -rf $(TARBALL) $(INSTALL_ROOT)

