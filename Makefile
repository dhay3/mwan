.PHONY: init package package-dir clean compile install sha1sum

APP_NAME ?= mwan
PYTHON ?= .conda/bin/python
PYINSTALLER ?= $(PYTHON) -m PyInstaller
ENTRYPOINT ?= src/__main__.py
DIST_DIR ?= dist
BUILD_DIR ?= build
DIST_DIR ?= $(DIST_DIR)

package:
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

oss:
	ossutil cp -f $(DIST_DIR)/$(APP_NAME) oss://cpd-swy/temp/hz.cheng/mwan/mwan --acl public-read

clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR)
