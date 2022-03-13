include private.mk

.PHONY: all
all: cutlist.pdf

.PHONY: blank
blank: CUTLIST_ARGS :=
blank: cutlist.pdf

cutlist.pdf: cutlist.svg
	convert $< $@

cutlist.svg: cutlist.py style.css Makefile private.mk
	python3 $< $(CUTLIST_ARGS)

.PHONY: debug
debug: CUTLIST_ARGS += --debug
debug: cutlist.pdf

.PHONY: clean
clean:
	git clean -dfx -e private.mk
