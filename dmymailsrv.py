#!/usr/bin/python -tt
# vi: ft=python et ts=4 sw=4 sts=0

import os
import sys
import syslog
import asyncore
from datetime import datetime
from optparse import OptionParser
from smtpd import SMTPServer, DebuggingServer
from email import FeedParser
from email.Header import decode_header

class DummyEmailServerBase(SMTPServer):
    def __init__(self, localaddr, remoteaddr, output_dir=None, convert=False,
                 log_via=None):
        SMTPServer.__init__(self, localaddr, None)

        if not output_dir:
            output_dir = '.'
        self.output_dir = output_dir

        self.convert = convert

        if not log_via:
            log_via = 'stdio'
        self.log_via = log_via

    def log(self, message, priority=None):
        if self.log_via == 'syslog':
            if not priority:
                priority = syslog.LOG_INFO
            syslog.syslog(priority, message)
        else:
            timestamp = datetime.now().strftime('[%Y/%m/%d %H:%M:%S] ')
            message = timestamp + message

            if priority == syslog.LOG_ERR:
                message = '[ERR] ' + message

            message += "\n"

            if self.log_via == 'file':
                logfile = os.path.normpath(os.path.join(self.output_dir,
                                                        'messages.log'))
                try:
                    f = open(logfile, 'a')
                    f.write(message)
                    f.close()
                except:
                    pass
            else:
                sys.stderr.write(message)

    def demime_message(self, data):
        parser = FeedParser.FeedParser()
        parser.feed(data)
        mail = parser.close()

        data = ''
        for k, v in mail.items():
            values = []
            for val, enc in decode_header(v):
                if enc == None:
                    values.append(val)
                else:
                    values.append(unicode(val, enc).encode('utf-8'))
            data += "%s: %s\n" % (k, ' '.join(values))

        data += "\n"
        charset = mail.get_param('charset')
        if charset == None:
            data += mail.get_payload()
        else:
            data += unicode(mail.get_payload(), charset).encode('utf-8')

        return data

class SimpleEmailServer(DummyEmailServerBase):
    def process_message(self, peer, mailfrom, rcpttos, data):
        info = 'From: %s, To: %s' % (mailfrom, ', '.join(rcpttos))

        now = datetime.now()
        filename = '%s.%06u.eml' % ( now.strftime('%Y%m%d_%H%M%S'),
                                     now.microsecond )
        fullpath = os.path.normpath(os.path.join(self.output_dir, filename))

        try:
            f = open(fullpath, 'w')
            if self.convert:
                f.write(self.demime_message(data))
            else:
                f.write(data)
            f.close()

            self.log('%s (%s) saved.' % (filename, info))
        except:
            self.log('%s (%s) failed.' % (filename, info), syslog.LOG_ERR)

class DumbEmailServer(DummyEmailServerBase):
    def process_message(self, peer, mailfrom, rcpttos, data):
        self.log('received From: %s, To: %s.' % (mailfrom, ', '.join(rcpttos)))

def run(address, port, server_type='simple', output_dir=None, convert=False,
        log_via='syslog'):

    args = {
        'localaddr':    (address, int(port)),
        'remoteaddr':   None,
        'output_dir':   output_dir,
        'convert':      convert,
        'log_via':      log_via,
    }

    if server_type == 'dumb':
        server_class = DumbEmailServer
    else:
        server_class = SimpleEmailServer

    if log_via == 'syslog':
        syslog.openlog('dmymailsrv', 0, syslog.LOG_DAEMON)

    server = server_class(**args)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass

def main():
    parser = OptionParser()

    parser.add_option('-a', '--address', dest='address', default='localhost',
                      help='listening address (default: localhost)')
    parser.add_option('-p', '--port', dest='port', default=25,
                      help='listening port    (default: 25)')
    parser.add_option('-d', '--outdir', dest='outdir', default='.',
                      help='output directory  (default: .)')
    parser.add_option('-c', '--convert', dest='convert', action='store_true',
                      help='will convert message encoding')
    parser.add_option('-n', '--dumb', dest='dumb', action='store_true',
                      help='will not save any messages locally')
    parser.add_option('-e', '--stderr', dest='log_via_stderr',
                      action='store_true',
                      help='output system messages via stderr' +
                           ' (default: syslog)')
    parser.add_option('-l', '--log-file', dest='log_via_file',
                      action='store_true',
                      help='output system messages to log file')

    options, argv = parser.parse_args()

    args = {
        'address':      options.address,
        'port':         options.port,
        'output_dir':   options.outdir,
        'convert':      options.convert,
    }

    if options.dumb:
        args['server_type'] = 'dumb'
    else:
        args['server_type'] = 'simple'

    if options.log_via_stderr:
        args['log_via'] = 'stderr'
    elif options.log_via_file:
        args['log_via'] = 'file'
    else:
        args['log_via'] = 'syslog'

    run(**args)

if __name__ == '__main__': main()

