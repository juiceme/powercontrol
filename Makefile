TARBALL = powercontrol.tar.gz
INSTALL_ROOT = ./installroot
USER_DIRECTORY = juice

build:
	mkdir -p $(INSTALL_ROOT)/home/$(USER_DIRECTORY)/.local/bin/
	mkdir -p $(INSTALL_ROOT)/home/$(USER_DIRECTORY)/.local/state/
	cp ./scripts/* $(INSTALL_ROOT)/home/$(USER_DIRECTORY)/.local/bin/
	tar cfz $(TARBALL) --owner=root --group=root -C $(INSTALL_ROOT) .

clean:
	rm -rf $(TARBALL) $(INSTALL_ROOT)/home

