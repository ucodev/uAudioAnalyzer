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
import signal
import multiprocessing
import subprocess
import time


class LSP():
    ### (L)oopback (S)ignal (P)ath ###

    # Properties

    __init_args = None      # Original __init__ arguments
    __refresh = None        # Refresh generator

    __filename_src = None   # Source signal file (wav required)
    __filename_dst = None   # Destination signal file (wav or raw)
    __fs = None             # Sampling frequency (recording)
    __length = None         # Length (recording)
    __channels = None       # Channels (recording)
    __ftype = None          # File type (wav or raw; recording)
    __fsubtype = None       # File subtype (wav or raw; recording)


    # Initializers, Loaders and Reloaders

    def __init__(self, filename_src = None, filename_dst = None, fs = 48000, length = 2, channels = 1, ftype = "raw", fsubtype = "S24_3LE", standalone = False, io_delay = 1.15):
        self.__init_args = [ filename_src, filename_dst, fs, length, channels, ftype, fsubtype, standalone, io_delay ]

        self.__refresh = self.load(*self.__init_args)

        try:
            self.refresh()
        except StopIteration:
            pass

    def load(self, filename_src = None, filename_dst = None, fs = 48000, length = 2, channels = 1, ftype = "raw", fsubtype = "S24_3LE", standalone = False, io_delay = 1.15):
        self.filename_src(filename_src)
        self.filename_dst(filename_dst)
        self.fs(fs)
        self.length(length)
        self.channels(channels)
        self.ftype(ftype)
        self.fsubtype(fsubtype)

        while True:
            if standalone is True:
                if self.filename_dst() is None or self.filename_src() is None:
                    raise Exception("When 'standalone' is True, both source and destination filenames must be provided.")

                self._process(io_delay = io_delay)

            yield

    def reload(self, standalone = False, io_delay = 1.15):
        self.__refresh = self.load(self.filename_src(), self.filename_dst(), self.fs(), self.length(), self.channels(), self.ftype(), self.fsubtype(), standalone, io_delay)

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

    def filename_src(self, src = None):
        if src is not None:
            self.__filename_src = src
            return self
        else:
            return self.__filename_src

    def filename_dst(self, dst = None):
        if dst is not None:
            self.__filename_dst = dst
            return self
        else:
            return self.__filename_dst

    def fs(self, freq = None):
        if freq is not None:
            self.__fs = freq
            return self
        else:
            return self.__fs

    def length(self, n = None):
        if n is not None:
            self.__length = n
            return self
        else:
            return self.__length

    def channels(self, n = None):
        if n is not None:
            self.__channels = n
            return self
        else:
            return self.__channels

    def ftype(self, ftype = None):
        if ftype is not None:
            self.__ftype = ftype
            return self
        else:
            return self.__ftype

    def fsubtype(self, fsubtype = None):
        if fsubtype is not None:
            self.__fsubtype = fsubtype
            return self
        else:
            return self.__fsubtype


    # Processors and Pre-Processors

    def _process(self, io_delay = 1.15):
        # TODO: This approach is far from ideal. It is currently serving
        # as duct tape to integrate with other functionalities.
        #
        # A low level library is being developed to replace the need of
        # external binaries and processes being called here.

        p = multiprocessing.Process(target = self.play)

        p.start()

        os.setpgid(p.pid, p.pid)

        time.sleep(io_delay)

        self.record()

        pid = p.pid

        p.terminate()

        os.killpg(os.getpgid(pid), signal.SIGTERM)


    # I/O

    def play(self, filename = None):
        if filename is None:
            if self.filename_src() is not None:
                filename = self.filename_src()
            else:
                raise Exception("No source file was specified.")

        # TODO: See _process() comments. This will be replaced.
        return subprocess.run([ "aplay", filename ], capture_output = True)

    def record(self, filename = None, fs = None, length = None, channels = None, ftype = None, fsubtype = None):
        if filename is None:
            if self.filename_dst() is not None:
                filename = self.filename_dst()
            else:
                raise Exception("No destination file was specified.")

        if fs is None:
            fs = self.fs()

        if length is None:
            length = self.length()

        if channels is None:
            channels = self.channels()

        if ftype is None:
            ftype = self.ftype()

        if fsubtype is None:
            fsubtype = self.fsubtype()

        # TODO: See _process() comments. This will be replaced.
        return subprocess.run([ "arecord", "-f", fsubtype, "-r", str(fs), "-d", str(int(length)), "-c", str(channels), "-t", ftype, filename ], capture_output = True)


