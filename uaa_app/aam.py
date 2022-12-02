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
#  - Frequency Domain Analyzer (FDA)
#  - Loopback Signal Path (LSP)
#  - Signal Data File (SDF)
#  - Sine Wave Generator (SWG)
#  - Time Domain Analyzer (TDA)
#
from uaa_core import FDA, LSP, SDF, SWG, TDA


class AAM():
    ### (A)pplication: (A)udio (M)eter ###

    # Properties

    __init_args = None  # Original __init__ arguments
    __refresh = None    # Refresh generator

    __cli = None        # CLI() object
    __dci = None        # DCI() object
    __tmp_dir = None    # temporary file storage location (directory path)


    # Initializers, Loaders and Reloaders

    def __init__(self, cli, dci, tmp_dir = "/tmp"):
        self.__init_args = [ cli, dci, tmp_dir ]

        self.__refresh = self.load(*self.__init_args)

        try:
            self.refresh()
        except StopIteration:
            pass

    def load(self, cli, dci, tmp_dir = "/tmp"):
        self.cli(cli)
        self.dci(dci)
        self.tmp_dir(tmp_dir)

        print("Press 'Ctrl+C' to exit...")

        while True:
            try:
                swg = SWG("%s/s_aam_test_%d.wav" % (self.tmp_dir(), self.cli().freq_base()), freqs = [ self.cli().freq_base() ], amplitudes = [ 1 ], length = 3.)
                lsp = LSP("%s/s_aam_test_%d.wav" % (self.tmp_dir(), self.cli().freq_base()), "%s/l_aam_test_%d.raw" % (self.tmp_dir(), self.cli().freq_base()), standalone = True, io_delay = 0.75, length = 1)

                sdf = SDF("%s/l_aam_test_%d.raw" % (self.tmp_dir(), self.cli().freq_base()), ftype = "raw", fs = 48000, bit_depth = 24)
                tda = TDA(sdf, dci, periods = False)
                fda = FDA(tda, dci)
            except KeyboardInterrupt:
                break

            print("dBFS: %.2f" % fda.spectrum_magn_db().max())
            print("Vrms: %.5f" % tda.vrms())
            print("Vpeak: %.5f" % tda.vpeak())
            print("SNR: %.2f" % fda.snr())
            print("")

            yield

        # Cleanup
        try:
            os.unlink("%s/s_aam_test_%d.wav" % (self.tmp_dir(), self.cli().freq_base()))
            os.unlink("%s/l_aam_test_%d.raw" % (self.tmp_dir(), self.cli().freq_base()))
        except Exception as e:
            raise Exception("Unable to cleanup temporary files: %s" % e)

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

    def dci(self, obj = None):
        if obj is not None:
            self.__dci = obj
            return self
        else:
            return self.__dci

    def tmp_dir(self, tdir = None):
        if tdir is not None:
            self.__tmp_dir = tdir
            return self
        else:
            return self.__tmp_dir


