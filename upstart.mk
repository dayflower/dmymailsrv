
INSTALL:=/usr/bin/install

all:	help

help:
	@echo "*** makefile for upstart ***"
	@echo "usage: sudo make install"

install:	install-bin install-upstart install-default setup-dir

install-bin:
	$(INSTALL) -c -m 755 dmymailsrv.py /usr/sbin/dmymailsrv

install-upstart:
	$(INSTALL) -c -m 755 upstart.conf /etc/init/dmymailsrv.conf

install-default:
	$(INSTALL) -c -m 644 sysconfig /etc/default/dmymailsrv

setup-dir:
	mkdir -p /var/lib/dmymail

.PHONY:		all help install
.PHONY:		install-bin install-upstart install-default setup-dir
