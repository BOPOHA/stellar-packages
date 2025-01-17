# required packages:
# dnf install rpmdevtools rpkg
.PHONY: epel7

PROJECTNAME=stellar-core
PROJECTTMPDIR=/tmp/$(PROJECTNAME)

clean:
	rm -rf $(PROJECTTMPDIR)

submodules:
	# https://github.com/stellar/stellar-core/compare/v20.1.0...v20.3.0
	bash -x update.submodules.sh

spec:
	rpkg spec --spec $(PROJECTNAME).spec -p

rpmbuild:
	spectool --get-files --directory $(PROJECTTMPDIR) $(PROJECTNAME).spec
	rpkg srpm --spec $(PROJECTNAME).spec --outdir $(PROJECTTMPDIR)
	rpmbuild --nocheck --rebuild $(PROJECTTMPDIR)/$(PROJECTNAME)-*.src.rpm

epel7:
	spectool --get-files --directory $(PROJECTTMPDIR) $(PROJECTNAME).spec
	rpkg srpm --spec $(PROJECTNAME).spec --outdir $(PROJECTTMPDIR)
	mock --enable-network --no-clean -r custom-epel-7-x86_64 --resultdir=rpm-results  $(PROJECTTMPDIR)/$(PROJECTNAME)-*.src.rpm
	# need file /etc/mock/custom-epel-7-x86_64.cfg with content:
	# include('templates/centos-7.tpl')
	# include('templates/epel-7.tpl')
	# config_opts['root'] = 'centos+epel+sclo-7-x86_64'
	# config_opts['description'] = 'CentOS 7 + EPEL + SCLO'
	# config_opts['target_arch'] = 'x86_64'
	# config_opts['legal_host_arches'] = ('x86_64',)
	# config_opts['chroot_setup_cmd'] += " llvm-toolset-7.0-clang rh-postgresql12-postgresql-devel rh-postgresql12-postgresql-server epel-release --disableincludes=all"

epel8:
	spectool --get-files --directory $(PROJECTTMPDIR) $(PROJECTNAME).spec
	rpkg srpm --spec $(PROJECTNAME).spec --outdir $(PROJECTTMPDIR)
	mock --no-clean --dnf --config-opts module_enable= --config-opts module_enable=postgresql:13 -r centos-stream+epel-8-x86_64 --resultdir=rpm-results  $(PROJECTTMPDIR)/$(PROJECTNAME)-*.src.rpm

fc39:
	spectool --get-files --directory $(PROJECTTMPDIR) $(PROJECTNAME).spec
	rpkg srpm --spec $(PROJECTNAME).spec --outdir $(PROJECTTMPDIR)
	mock --no-clean --dnf -r fedora-38-x86_64 --resultdir=rpm-results  $(PROJECTTMPDIR)/$(PROJECTNAME)-*.src.rpm
