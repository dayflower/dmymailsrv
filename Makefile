ifeq ($(shell ls -d /etc/init 2>/dev/null),)
has_upstart:=0
else
has_upstart:=1
endif

ifneq ($(UPSTART),)
has_upstart:=1
endif

ifneq ($(SYSV),)
has_upstart:=0
endif

ifeq ($(has_upstart),1)
include upstart.mk
else
include rc.mk
endif
