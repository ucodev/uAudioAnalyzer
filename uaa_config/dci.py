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
import json


class DCI():
    ### (D)evice (C)alibration (I)nterface ###

    # Properties

    __init_args = None   # Original __init__ arguments
    __refresh = None     # Refresh generator

    __cal_data = None         # Construct argument #1
    __cal_file = None         # Construct argument #2
    __cache = None            # Construct argument #3
    __write = None            # If this is a write operation, 1 Vrms is expected at the input. Calibration file will be overwritten
    __npeak = None            # Normalized peak value of 1 Vrms
    __nrms = None             # Normalized 1 Vrms
    __nfullscale = None       # Normalized fullscale (the normalized maximum amplitude that repesents 0 dBFS for the device)
    __impedance = None        # Line Impedance (for dBu / dBm / dBFS calculation)
    __log_unit = None         # Log scale unit ("dBu", "dBm", "dBFS", ...)
    __log_unit_adjust = None  # Log unit magnitude adjustment (30dB for dBu or dBm, as 1000 mW == 1 W)
    __log_0dB_adjust = None   # If a fullscale reference is used, such as dBFS, this indicates the maximum dBu or dBm of the system
    __log_offset = None       # Log scale offset (for convertion between dBu -> dBFS, or dBm -> dBFS)


    # Initializers, Loaders and Reloaders

    def __init__(self, cal_data = None, cal_file = "cal.json", cache = True, write = False):
        self.__init_args = [ cal_data, cal_file, cache, write ]

        self.__refresh = self.load(*self.__init_args)

        try:
            self.refresh()
        except StopIteration:
            pass

    def load(self, cal_data = None, cal_file = "cal.json", cache = True, write = False):
        local_cache = None

        self.cal_data(cal_data)
        self.cal_file(cal_file)
        self.cache(cache)
        self.write(write)

        while True:
            if local_cache is True:
                yield
                continue

            if write is False:
                if cal_data is None:
                    if not os.path.isfile(cal_file):
                        raise Exception("No calibration file found: %s" % cal_file)

                    with open(cal_file, "r") as f:
                        try:
                            cal_data = json.loads(f.read())
                        except Exception:
                            raise Exception("Unable to decode calibration data from file: %s" % cal_file)

                for k in ("npeak", "nrms", "nfullscale", "impedance", "log_0dB_adjust", "log_unit_adjust", "log_unit"):
                    if k not in cal_data:
                        raise Exception("Missing property in calibration data: %s" % k)

                # Set the log offset that will be used in dB magnitude calculations
                cal_data["log_offset"] = cal_data["log_unit_adjust"] - cal_data['log_0dB_adjust']

                self.cal_data(cal_data)

            self._process()

            yield

            if cache is True: local_cache = True

    def reload(self):
        self.__refresh = self.load(self.cal_data(), self.cal_file(), self.cache())

        try:
            self.refresh()
        except StopIteration:
            pass

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

    def cal_data(self, data = None):
        if data is not None:
            self.__cal_data = data
            return self
        else:
            return self.__cal_data

    def cal_file(self, file = None):
        if file is not None:
            self.__cal_file = file
            return self
        else:
            return self.__cal_file

    def cache(self, status = None):
        if status is not None:
            self.__cache = status
            return self
        else:
            return self.__cache

    def write(self, status = None):
        if status is not None:
            self.__write = status
            return self
        else:
            return self.__write

    def npeak(self, peak = None):
        if peak is not None:
            self.__npeak = peak
            return self
        else:
            return self.__npeak

    def nrms(self, rms = None):
        if rms is not None:
            self.__rms = rms
            return self
        else:
            return self.__rms

    def nfullscale(self, fullscale = None):
        if fullscale is not None:
            self.__nfullscale = fullscale
            return self
        else:
            return self.__nfullscale

    def impedance(self, z = None):
        if z is not None:
            self.__impedance = z
            return self
        else:
            return self.__impedance

    def log_unit(self, unit = None):
        if unit is not None:
            self.__log_unit = unit
            return self
        else:
            return self.__log_unit

    def log_unit_adjust(self, adjust = None):
        if adjust is not None:
            self.__log_unit_adjust = adjust
            return self
        else:
            return self.__log_unit_adjust

    def log_0dB_adjust(self, adjust = None):
        if adjust is not None:
            self.__log_0dB_adjust = adjust
            return self
        else:
            return self.__log_0dB_adjust

    def log_offset(self, offset = None):
        if offset is not None:
            self.__log_offset = offset
            return self
        else:
            return self.__log_offset


    # Processors and Pre-Processors

    def _process(self):
        if self.write() is True:
            self.write_cal()
        else:
            self.npeak(self.cal_data()['npeak'])
            self.nrms(self.cal_data()['nrms'])
            self.nfullscale(self.cal_data()['nfullscale'])
            self.impedance(self.cal_data()['impedance'])
            self.log_unit(self.cal_data()['log_unit'])
            self.log_unit_adjust(self.cal_data()['log_unit_adjust'])
            self.log_0dB_adjust(self.cal_data()['log_0dB_adjust'])
            self.log_offset(self.cal_data()['log_offset'])


    # I/O

    def write_cal(self):
        try:
            with open(self.cal_file(), "w+") as f:
                f.write(json.dumps(self.cal_data()))
        except Exception as e:
            raise Exception("Unable to write to file %s: %s" % (self.cal_file(), e))


