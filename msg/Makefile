DESTDIR=./

all: build-stamp

build-stamp:
	cd ..; xgettext -o msg/cycle.pot *.py
	for f in *.po; do i=`echo $$f | awk 'BEGIN {FS="."} {print $$1}'`; echo Building Language \"$$i\"; msgfmt $$f -o $$i.mo; done
	touch build-stamp

clean:
	#for f in *.po; do i=`echo $$f | awk 'BEGIN {FS="."} {print $$1}'`; rm -rf "$$i"; done
	rm -f *.mo
	rm -f cycle.pot
	rm -f build-stamp

install: build-stamp
	for f in *.mo; do i=`echo $$f | awk 'BEGIN {FS="."} {print $$1}'`; echo Installing Language \"$$i\"; install -d $(DESTDIR)/locale/$$i; install -p -d -m 755 $(DESTDIR)/locale/$$i/LC_MESSAGES; install -m 644 $$f $(DESTDIR)/locale/$$i/LC_MESSAGES/cycle.mo; done
