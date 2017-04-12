PKG_NAME = aiaiai
SPECFILE = $(addsuffix .spec, $(PKG_NAME))
PKG_VERSION := $(shell grep '^Version: ' $(SPECFILE)|awk '{print $$2}')
TARBALL := $(PKG_NAME)-$(PKG_VERSION).tar.bz2

tarball:
	@rm -f *.tar.bz2
	@cd .. && git archive --prefix $(PKG_NAME)-$(PKG_VERSION)/ HEAD | gzip > packaging/$(TARBALL)

rpm: tarball
	@rm -f *.rpm
	rpmbuild -bs $(SPECFILE) --define "_sourcedir $(shell pwd)" \
		--define "_srcrpmdir $(shell pwd)" \

all: tarball rpm

clean:
	-rm -f *.tar.bz2 *.rpm
