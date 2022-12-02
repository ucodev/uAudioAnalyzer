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
#  - Signal Data File (SDF)
#  - Sine Wave Generator (SWG)
#
from uaa_core import LSP, SDF, SWG


class AIC():
    ### Application: Interface Calibration ###

    # Properties

    __init_args = None  # Original __init__ arguments
    __refresh = None    # Refresh generator

    __cli = None        # CLI() object
    __tmp_dir = None    # temporary file storage location (directory path)


    # Initializers, Loaders and Reloaders

    def __init__(self, cli, tmp_dir = "/tmp"):
        self.__init_args = [ cli, tmp_dir ]

        self.__refresh = self.load(*self.__init_args)

        try:
            self.refresh()
        except StopIteration:
            pass

    def load(self, cli, tmp_dir = "/tmp"):
        self.cli(cli)
        self.tmp_dir(tmp_dir)

        cal_data = {}

        while True:
            # Process 1 Vrms
            self.stage_acquire_signal("1 Vrms")
            cal_data['nrms'], cal_data['npeak'] = self.stage_process_signal()

            # Process Full-Scale
            self.stage_acquire_signal("Full-Scale")
            cal_data['nfullscale'] = self.stage_process_signal()[0]

            # Process unit of power
            cal_data['log_unit'], cal_data['impedance'], cal_data['log_unit_adjust'], cal_data['log_0dB_adjust'] = self.stage_power_unit(cal_data)

            # Write calibration file
            dci = DCI(cal_data, self.cli().cal_file(), write = True)

            # Cleanup
            self.stage_cleanup()

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

    def tmp_dir(self, tdir = None):
        if tdir is not None:
            self.__tmp_dir = tdir
            return self
        else:
            return self.__tmp_dir


    # Stages

    def stage_acquire_signal(self, input_type_str = "1 Vrms"):
        print("\n\n === %s Calibration ===" % input_type_str)

        try:
            input("\n => Press 'Enter' to generate a %s Hz signal. 'Ctrl+C' to abort..." % self.cli().freq_base())
        except KeyboardInterrupt:
            print("Aborted.")
            return

        swg = SWG("%s/s_cal_%d.wav" % (self.tmp_dir(), self.cli().freq_base()), freqs = [ self.cli().freq_base() ], amplitudes = [ 1 ], length = 5.)
        lsp = LSP("%s/s_cal_%d.wav" % (self.tmp_dir(), self.cli().freq_base()))

        print("\n => Adjust the signal level to match %s, then press Ctrl+C" % input_type_str)

        while True:
            try:
                lsp.play()
            except KeyboardInterrupt:
                break

        try:
            input("\n => Connect the %s output signal to an input with gain set to minimum... Press 'Enter' to continue, 'Ctrl+C' to abort...\n" % input_type_str)
        except KeyboardInterrupt:
            print("Aborted.")
            return

        print("\n => Wait a few seconds while calibration signal is being recorded...")

        lsp = LSP("%s/s_cal_%d.wav" % (self.tmp_dir(), self.cli().freq_base()), "%s/d_cal_%d.raw" % (self.tmp_dir(), self.cli().freq_base()), standalone = True)

    def stage_process_signal(self):
        sdf = SDF("%s/d_cal_%d.raw" % (self.tmp_dir(), self.cli().freq_base()), ftype = "raw", fs = 48000, bit_depth = 24)

        if not sdf.normalized():
            raise Exception("Source signal is not normalized between [ -1., 1. ].")

        assert(sdf.signal().min() >= -1 and sdf.signal().max() <= 1)

        nrms = np.sqrt(np.sum(np.power(sdf.signal(), 2)) / sdf.signal().size)
        npeak = sdf.signal().max()

        return (nrms, npeak)

    def stage_power_unit(self, cal_data):
        print("\n => Select the unit of power:\n")
        print("    1. dBFS")
        print("    2. dBVU")
        print("    3. dBu")
        print("    4. dBV")
        print("    5. dBm")

        while True:
            c = input("\n    Choice [1-5]: ") or None

            if not c: continue

            try:
                c = int(c)
            except ValueError:
                continue

            if c not in range(1, 6): continue
            
            break

        print("")

        if c == 1:
            return ("dBFS", 600., 30., 10 * np.log10(((cal_data['nfullscale'] / cal_data['nrms']) ** 2) / 600.) + 30)
        elif c == 2:
            return ("dBVU", 600., 30., 4.)
        elif c == 3:
            return ("dBu", 600., 30., 0.)
        elif c == 4:
            return ("dBV", 1000., 30., 0.)
        elif c == 5:
            return ("dBm", 50., 30., 0.)
        else:
            raise Exception("Invalid selection for unit of power")

    def stage_cleanup(self):
        try:
            os.unlink("%s/s_cal_%d.wav" % (self.tmp_dir(), self.cli().freq_base()))
            os.unlink("%s/d_cal_%d.raw" % (self.tmp_dir(), self.cli().freq_base()))
        except Exception as e:
            raise Exception("Unable to cleanup temporary files: %s" % e)


