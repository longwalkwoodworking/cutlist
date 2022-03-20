# Copyright © 2022 Eric Diven
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details. */

include private.mk

.PHONY: all
all: cutlist.svg

.PHONY: blanks
blanks: blank-ledger.svg blank-a3.svg

blank-ledger.svg: CUTLIST_ARGS :=
blank-ledger.svg: cutlist.svg

blank-a3.svg: CUTLIST_ARGS := --paper=a3
blank-a3.svg: cutlist.svg

%.svg: cutlist.py style.css Makefile private.mk
	python3 $< $(CUTLIST_ARGS) $@

.PHONY: debug
debug: CUTLIST_ARGS += --debug
debug: cutlist.svg

.PHONY: clean
clean:
	git clean -dfx -e private.mk
