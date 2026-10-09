# required packages:
# dnf install mock rpmdevtools rpkg
.PHONY: clean submodules spec rust-spec sources srpm rust-srpm \
	rpmbuild rpmbuild-rust rpmbuild-tests fc44 fc44-core fc44-rust fc44-tests

PROJECTNAME=stellar-core
RUSTPROJECTNAME=stellar-core-rust
PROJECTTMPDIR=/tmp/stellar-core-split-rpm
RESULTDIR=$(CURDIR)/rpm-results
CHAINREPO=$(RESULTDIR)/fc44-chain

clean:
	rm -rf $(PROJECTTMPDIR)

$(PROJECTTMPDIR):
	mkdir -p $(PROJECTTMPDIR)

submodules:
	# https://github.com/stellar/stellar-core/compare/v20.3.0...v29.0.0
	bash -x update.submodules.sh

spec:
	rpkg spec --spec $(PROJECTNAME).spec -p

rust-spec:
	rpkg spec --spec $(RUSTPROJECTNAME).spec -p

sources: | $(PROJECTTMPDIR)
	spectool --get-files --directory $(PROJECTTMPDIR) $(PROJECTNAME).spec

srpm: sources
	rpkg srpm --spec $(PROJECTNAME).spec --outdir $(PROJECTTMPDIR)
	ln -sfn "$$(ls -t $(PROJECTTMPDIR)/$(PROJECTNAME)-[0-9]*.src.rpm | head -n 1)" \
		$(PROJECTTMPDIR)/$(PROJECTNAME).src.rpm

rust-srpm: sources
	rpkg srpm --spec $(RUSTPROJECTNAME).spec --outdir $(PROJECTTMPDIR)
	ln -sfn "$$(ls -t $(PROJECTTMPDIR)/$(RUSTPROJECTNAME)-[0-9]*.src.rpm | head -n 1)" \
		$(PROJECTTMPDIR)/$(RUSTPROJECTNAME).src.rpm

rpmbuild-rust: rust-srpm
	command -v ccache >/dev/null
	command -v sccache >/dev/null
	rpmbuild --define '_with_compiler_cache 1' --nocheck --rebuild $(PROJECTTMPDIR)/$(RUSTPROJECTNAME).src.rpm

rpmbuild: srpm
	command -v ccache >/dev/null
	command -v sccache >/dev/null
	rpm -q $(RUSTPROJECTNAME)-static
	rpmbuild --define '_with_compiler_cache 1' --nocheck --rebuild $(PROJECTTMPDIR)/$(PROJECTNAME).src.rpm

rpmbuild-tests: srpm
	command -v ccache >/dev/null
	command -v sccache >/dev/null
	rpmbuild --with tests --define '_with_compiler_cache 1' --rebuild $(PROJECTTMPDIR)/$(PROJECTNAME).src.rpm

fc44: rust-srpm srpm
	mock --enable-network -r fedora-44-x86_64 --chain \
		--localrepo=$(CHAINREPO) \
		$(PROJECTTMPDIR)/$(RUSTPROJECTNAME).src.rpm \
		$(PROJECTTMPDIR)/$(PROJECTNAME).src.rpm

fc44-core: srpm
	mock --enable-network -r fedora-44-x86_64 --chain \
		--localrepo=$(CHAINREPO) \
		$(PROJECTTMPDIR)/$(PROJECTNAME).src.rpm

fc44-rust: rust-srpm
	mock --enable-network --no-clean -r fedora-44-x86_64 \
		--resultdir=$(RESULTDIR)/fc44-rust \
		$(PROJECTTMPDIR)/$(RUSTPROJECTNAME).src.rpm

fc44-tests: srpm
	mock --enable-network --no-clean --with tests -r fedora-44-x86_64 \
		--resultdir=$(RESULTDIR)/fc44-tests \
		$(PROJECTTMPDIR)/$(PROJECTNAME).src.rpm
