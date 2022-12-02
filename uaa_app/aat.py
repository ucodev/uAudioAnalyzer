#!/usr/bin/env python3
#
#
#    uCodev Audio Analyzer (uAudioAnalyzer)
#    Copyright (C) 2022  Pedro A. Hortas <pah@ucodev.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#


import os

#
# import core interfaces
#
#  - Loopback Signal Path (LSP)
#  - Sine Wave Generator (SWG)
#
from uaa_core import LSP, SWG


try:
    _DEBUG_ENABLE
except NameError:
    _DEBUG_ENABLE = True


class AAT():
    ### Application: Audio Test ###

    # Properties

    __init_args = None  # Original __init__ arguments
    __refresh = None    # Refresh generator

    __cli = None        # CLI() object
    __cci = None        # CCI() object


    # Initializers, Loaders and Reloaders

    def __init__(self, cli, cci, freq_start = 15, freq_stop = 24000):
        self.__init_args = [ cli, cci, freq_start, freq_stop ]

        self.__refresh = self.load(*self.__init_args)

        try:
            self.refresh()
        except StopIteration:
            pass

    def load(self, cli, cci, freq_start = 15, freq_stop = 24000):
        self.cli(cli)
        self.cci(cci)

        if not os.path.isdir(self.cli().directory()):
            try:
                os.makedirs(self.cli().directory(), exist_ok = True)
            except Exception as e:
                raise Exception("Failed to create directory: %s" % e)

        while True:
            for f in self.cci().config()["common"]["test_freqs"]:
                if f < freq_start:
                    continue

                if f > freq_stop:
                    break

                if _DEBUG_ENABLE: print("Testing frequency: %d Hz" % f)
                swg = SWG("%s/s_%s.wav" % (self.cli().directory(), f), freqs = [ f ], amplitudes = [ 1 ], length = 5.)
                lsp = LSP("%s/s_%s.wav" % (self.cli().directory(), f), "%s/l_%s.raw" % (self.cli().directory(), f), standalone = True, io_delay = 1.15)

            yield

    def reload(self):
        raise Exception("Not implemented.")

    def refresh(self):
        # NOTE: __next__ is not implemented in the class itself to avoid
        #       the temptation of using next() for the class object.
        #       Future implementations of refresh() may not depend on
        #       internal generators. This way, calling refresh() will
        #       always be portable, regardless of how it is implemented
        #       internally.
        next(self.__refresh)


    # Setters and Getters
    #
    # NOTE: The built-in decorator @property is not used here so all
    #       setters/getters defined in this file are consistent with other
    #       complex forms of setters/getters used throughout the rest
    #       of this project.
    #
    # NOTE: It is possible, however, that this might change to @property in
    #       the future.

    def cli(self, obj = None):
        if obj is not None:
            self.__cli = obj
            return self
        else:
            return self.__cli

    def cci(self, obj = None):
        if obj is not None:
            self.__cci = obj
            return self
        else:
            return self.__cci


