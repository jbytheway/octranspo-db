CONVERTER := tools/zip2sqlite
SCRIPTS := $(wildcard tools/*.py $(CONVERTER))
ROOT := octranspo_data
ZIP := data/$(ROOT).zip

DOWNLOAD = wget -O $(ZIP) http://www.octranspo1.com/files/google_transit.zip

$(ROOT).sqlite.gz: data/$(ROOT).sqlite
	mkdir -p $(dir $@)
	gzip -c $< > $@

data/$(ROOT).sqlite: data/$(ROOT).zip $(SCRIPTS)
	$(CONVERTER) $< $@
	sqlite3 $@ analyze
	sqlite3 $@ "vacuum full;"

data/$(ROOT).zip:
	mkdir -p $(dir $@)
	$(DOWNLOAD)

download:
	mkdir -p $(dir $@)
	$(DOWNLOAD)

.DELETE_ON_ERROR:
