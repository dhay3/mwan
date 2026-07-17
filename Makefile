.PHONY: binary dpkg sha1sum oss clean

APP_NAME ?= mwan
VERSION ?= 1.0.0
PYTHON ?= .conda/bin/python
PYINSTALLER ?= $(PYTHON) -m PyInstaller
ENTRYPOINT ?= src/__main__.py
DIST_DIR ?= dist
BUILD_DIR ?= build
DEB_ARCH ?= $(shell uname -m | sed -e 's/^x86_64$$/amd64/' -e 's/^aarch64$$/arm64/' -e 's/^armv7l$$/armhf/')
APP_BINARY := $(DIST_DIR)/$(APP_NAME)
DEB_PACKAGE := $(DIST_DIR)/$(APP_NAME)_$(VERSION)_$(DEB_ARCH).deb
APP_SHA1 := $(APP_BINARY).sha1
DEB_SHA1 := $(DEB_PACKAGE).sha1
OSS_DIR ?= oss://cpd-swy/temp/hz.cheng/mwan

binary:
	$(PYINSTALLER) \
		--clean \
		--noconfirm \
		--onefile \
		--name $(APP_NAME) \
		--paths src \
		--distpath $(DIST_DIR) \
		--workpath $(BUILD_DIR)/pyinstaller \
		--specpath $(BUILD_DIR) \
		$(ENTRYPOINT)

dpkg: binary
	./scripts/build-deb.sh $(VERSION)

sha1sum: dpkg
	cd $(DIST_DIR) && sha1sum $(notdir $(APP_BINARY)) > $(notdir $(APP_SHA1))
	cd $(DIST_DIR) && sha1sum $(notdir $(DEB_PACKAGE)) > $(notdir $(DEB_SHA1))

clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR)

oss: sha1sum
	ossutil cp -f $(APP_BINARY) $(OSS_DIR)/$(APP_NAME) --acl public-read
	ossutil cp -f src/$(APP_NAME).toml $(OSS_DIR)/$(APP_NAME).toml --acl public-read
	ossutil cp -f src/$(APP_NAME).service $(OSS_DIR)/$(APP_NAME).service --acl public-read
	ossutil cp -f scripts/install.sh $(OSS_DIR)/install.sh --acl public-read
	ossutil cp -f $(DEB_PACKAGE) $(OSS_DIR)/$(notdir $(DEB_PACKAGE)) --acl public-read
	ossutil cp -f $(APP_SHA1) $(OSS_DIR)/$(notdir $(APP_SHA1)) --acl public-read
	ossutil cp -f $(DEB_SHA1) $(OSS_DIR)/$(notdir $(DEB_SHA1)) --acl public-read
