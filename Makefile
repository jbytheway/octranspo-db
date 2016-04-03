CONVERTER := tools/zip2sqlite
SCRIPTS := $(wildcard tools/*.py $(CONVERTER))
ROOT := octranspo_data

$(ROOT).sqlite.gz: data/$(ROOT).sqlite
	mkdir -p $(dir $@)
	gzip -c $< > $@

data/$(ROOT).sqlite: data/$(ROOT).zip $(SCRIPTS)
	$(CONVERTER) $< $@
	sqlite3 $@ analyze
	sqlite3 $@ "vacuum full;"

data/$(ROOT).zip:
	mkdir -p $(dir $@)
	wget -O $@ http://www.octranspo1.com/files/google_transit.zip

.DELETE_ON_ERROR:
