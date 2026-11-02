PERIOD ?= 4.0

test:
	$(MAKE) -C tb TOP=regfile  DEPTH=8 NREAD=2 BYPASS=0
	$(MAKE) -C tb TOP=mmio_top DEPTH=8 NREAD=2 BYPASS=0

test-all:
	@for top in regfile mmio_top; do for d in 8 16 32 64; do for r in 1 2 4; do for b in 0 1; do \
	  echo "== $$top D=$$d R=$$r B=$$b"; \
	  $(MAKE) -s -C tb TOP=$$top DEPTH=$$d NREAD=$$r BYPASS=$$b > /tmp/t.log 2>&1; \
	  grep -q "FAIL=0" /tmp/t.log || { tail -40 /tmp/t.log; exit 1; }; \
	done; done; done; done; echo ALL PASS

sweep:
	python3 scripts/sweep.py --period $(PERIOD) --jobs 1

parse:
	python3 scripts/parse.py

analyse:
	python3 scripts/analyse.py

.PHONY: test test-all sweep parse analyse
