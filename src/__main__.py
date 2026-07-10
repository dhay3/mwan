#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import mwan


if __name__ == "__main__":
    try:
        sys.exit(mwan.main())
    except KeyboardInterrupt:
        sys.exit(0)
