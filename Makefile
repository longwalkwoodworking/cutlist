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

blank-a3.svg: CUTLIST_ARGS := --paper=a3

%.svg: cutlist.py style.css Makefile private.mk
	python3 $< $(CUTLIST_ARGS) $@

.PHONY: debug
debug: CUTLIST_ARGS += --debug
debug: cutlist.svg

.PHONY: clean
clean:
	git clean -dfx -e private.mk

# IMPORTANT: DO NOT list private.mk.example as a prequisite of private.mk
# If private.mk.example is updated in the future, this will blow away the
# user's private.mk file, which likely has their customizations in it.
private.mk:
	cp private.mk.example private.mk
