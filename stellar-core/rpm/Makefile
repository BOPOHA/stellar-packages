# required packages:
# dnf install mock rpmdevtools rpkg
.PHONY: clean submodules spec srpm rpmbuild fc44

PROJECTNAME=stellar-core
PROJECTTMPDIR=/tmp/$(PROJECTNAME)

clean:
	rm -rf $(PROJECTTMPDIR)

$(PROJECTTMPDIR):
	mkdir -p $(PROJECTTMPDIR)

submodules:
	# https://github.com/stellar/stellar-core/compare/v20.3.0...v29.0.0
	bash -x update.submodules.sh

spec:
	rpkg spec --spec $(PROJECTNAME).spec -p

srpm: | $(PROJECTTMPDIR)
	spectool --get-files --directory $(PROJECTTMPDIR) $(PROJECTNAME).spec
	rpkg srpm --spec $(PROJECTNAME).spec --outdir $(PROJECTTMPDIR)

rpmbuild: srpm
	rpmbuild --nocheck --rebuild $(PROJECTTMPDIR)/$(PROJECTNAME)-*.src.rpm

fc44: srpm
	mock --enable-network --no-clean -r fedora-44-x86_64 --resultdir=rpm-results $(PROJECTTMPDIR)/$(PROJECTNAME)-*.src.rpm
