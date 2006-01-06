# -*- Mode: Python; coding: iso-8859-1 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Stoqdrivers
## Copyright (C) 2005 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
## USA.
##
## Author(s):   Johan Dahlin     <jdahlin@async.com.br>
##

from serial import Serial, EIGHTBITS, PARITY_NONE, STOPBITS_ONE

from stoqdrivers.log import Logger

class SerialBase(Serial, Logger):
    log_domain = 'serial'

    # All commands will have this prefixed
    CMD_PREFIX = '\x1b'
    CMD_SUFFIX = ''

    # used by readline()
    EOL_DELIMIT = '\r'

    # Set this attribute to avoid sending data to printer
    DEBUG_MODE = 0

    def __init__(self, device, baudrate=9600, bytesize=EIGHTBITS,
                 parity=PARITY_NONE, stopbits=STOPBITS_ONE):
        Logger.__init__(self)
        
        self.info('opening device %s' % device)
        Serial.__init__(self, device, baudrate=baudrate,
                        bytesize=bytesize, parity=parity,
                        stopbits=stopbits)
        self.setDTR(True)
        self.flushInput()
        self.flushOutput()
        self.setTimeout(3)

    def read_insist(self, n_bytes):
        """
        This is a more insistent read, that will try to read that many
        bytes a determined number of times.
        """
        number_of_tries = 12
        data = ""
        while True:
            data_left = n_bytes - len(data)
            if (data_left > 0) and (number_of_tries > 0):
                data += Serial.read(self, data_left)
                data_left = n_bytes - len(data)
                number_of_tries -= 1
            else:
                break

        return data
    
    def readline(self):
        if self.DEBUG_MODE:
            return
        c = ''
        out = ''
        while True:
            c = self.read(1)
            if c == self.EOL_DELIMIT:
                self.debug('<<< %r' % out)
                return out
            out +=  c

    def write(self, data):
        self.debug(">>> %r (%dbytes)" % (data, len(data)))
        Serial.write(self, data)

    def writeline(self, data):
        if self.DEBUG_MODE:
            return
        self.write(self.CMD_PREFIX + data + self.CMD_SUFFIX)
        return self.readline()

    def handle_error(self, error, command):
        """
        Should be implemented by subclass
        
        @param error:
        @param command:
        """
        raise NotImplementedError
