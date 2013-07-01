
INSTALL:=/usr/bin/install
CHKCONFIG:=/sbin/chkconfig

all:	help

help:
	@echo "*** makefile for sysv-rc ***"
	@echo "usage: sudo make install"

install:	install-bin install-initrc install-sysconfig setup-dir

install-bin:
	$(INSTALL) -c -m 755 -t /usr/sbin dmymailsrv

install-initrc:
	$(INSTALL) -c -m 755 initrc /etc/init.d/dmymailsrv
	$(CHKCONFIG) --add dmymailsrv

install-sysconfig:
	$(INSTALL) -c -m 644 sysconfig /etc/sysconfig/dmymailsrv

setup-dir:
	mkdir -p /var/lib/dmymail

.PHONY:		all help install
.PHONY:		install-bin install-initrc install-sysconfig setup-dir
