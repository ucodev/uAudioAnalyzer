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


class CLI():
    ### (C)ommand (L)ine (I)nterface ###

    # Properties

    __init_args = None  # Original __init__ arguments
    __refresh = None    # Refresh generator

    __argv = None       # Command Line Arguments Vector
    __argc = None       # Command Line Arguments Counter
    __operation = None  # Argument: operation
    __filename = None   # Argument: file name
    __directory = None  # Argument: directory
    __filetype = None   # Argument: file type
    __fs = None         # Argument: sampling frequency
    __bit_depth = None  # Argument: bit depth
    __blocksize = None  # Argument: block size
    __freq_base = None  # Argument: base frequency
    __cal_file = None   # Argument: calibration file


    # Initializers, Loaders and Reloaders

    def __init__(self, argv = None, cache = True):
        if argv is None:
            return

        self.__init_args = [ argv, cache ]

        self.__refresh = self.load(*self.__init_args)

        try:
            self.refresh()
        except StopIteration:
            pass

    def load(self, argv = None, cache = True):
        local_cache = None

        while True:
            if local_cache is True:
                yield
                continue

            if type(argv) != list:
                raise Exception("Invalid data type for 'argv' detected: %s" % type(argv))

            self.argv(argv)
            self.argc(len(argv))
            self._process()

            yield

            if cache is True: local_cache = True

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

    def argv(self, args = None, full = False, n = 0):
        if args is not None:
            self.__argv = args
            return self

        if self.__argv is not None:
            if full is False:
                if n >= 0 and n < len(self.__argv):
                    return self.__argv[n]
                else:
                    raise Exception("The requested argument vector index is outside of the existing boundaries")
            else:
                return self.__argv
        else:
            raise Exception("The argument vector data is not initialized.")

    def argc(self, n = None):
        if n is not None:
            self.__argc = n
            return self
        else:
            return self.__argc

    def operation(self, op = None):
        if op is not None:
            if op not in ("analyze", "calibrate", "meter", "test"):
                raise Exception("Invalid operation: %s" % op)

            self.__operation = op

            return self
        else:
            return self.__operation

    def filename(self, fname = None, validate = False):
        if fname is not None:
            if not os.path.isfile(fname) and validate is True:
                raise Exception("Invalid or non-existing file name: %s" % fname)

            self.__filename = fname

            return self
        else:
            return self.__filename

    def directory(self, dname = None, validate = False):
        if dname is not None:
            if not os.path.isdir(dname) and validate is True:
                raise Exception("Invalid or non-existing directory name: %s" % dname)

            self.__directory = dname

            return self
        else:
            return self.__directory

    def filetype(self, ftype = None):
        if ftype is not None:
            if ftype not in ("wav", "raw"):
                raise Exception("Invalid file type: %s" % ftype)

            self.__filetype = ftype

            return self
        else:
            return self.__filetype

    def fs(self, freq = None):
        if freq is not None:
            try:
                freq = int(freq)

                if freq <= 0: raise Exception()
            except Exception:
                raise Exception("Invalid sampling frequency: %s" % freq)

            self.__fs = int(freq)

            return self
        else:
            return self.__fs

    def bit_depth(self, n = None):
        if n is not None:
            try:
                n = int(n)

                if n < 8: raise Exception()
            except Exception:
                raise Exception("Invalid bit depth: %s" % n)

            self.__bit_depth = int(n)

            return self
        else:
            return self.__bit_depth

    def blocksize(self, n = None):
        if n is not None:
            try:
                n = int(n)

                if n < 0: raise Exception()
            except Exception:
                raise Exception("Invalid block size: %s" % n)

            self.__blocksize = n

            return self
        else:
            return self.__blocksize

    def freq_base(self, freq = None):
        if freq is not None:
            try:
                freq = int(freq)

                if freq < 0: raise Exception()
            except Exception:
                raise Exception("Invalid frequency: %s" % freq)

            self.__freq_base = freq

            return self
        else:
            return self.__freq_base

    def cal_file(self, file = None):
        if file is not None:
            self.__cal_file = file
            return self
        else:
            return self.__cal_file


    # Processors and Pre-Processors

    def _process(self):
        if self.argc() < 3:
            raise Exception("Invalid syntax.")

        self.operation(self.argv(n = 1))

        if self.operation() == "test":
            if self.argc() != 3:
                raise Exception("Invalid syntax for 'test' operation.")

            self.parse_op_test()
        elif self.operation() == "meter":
            if self.argc() != 3:
                raise Exception("Invalid syntax for 'read' operation.")

            self.parse_op_meter()
        elif self.operation() == "analyze":
            if self.argc() < 4:
                raise Exception("Invalid syntax for 'analyze' operation.")

            self.parse_op_analyze()
        elif self.operation() == "calibrate":
            if self.argc() != 4:
                raise Exception("Invalid syntax for 'calibrate' operation.")

            self.parse_op_calibrate()
        else:
            raise Exception("Unknown operation: %s" % self.operation())


    # Parsers

    def parse_op_test(self):
        self.directory(self.argv(n = 2))

    def parse_op_meter(self):
        self.freq_base(self.argv(n = 2))

    def parse_op_analyze(self):
        if os.path.isfile(self.argv(n = 2)):
            self.filename(self.argv(n = 2), validate = True)
        elif os.path.isdir(self.argv(n = 2)):
            self.directory(self.argv(n = 2), validate = True)
        else:
            raise Exception("Requested path doesn't point to an existing filename nor directory")

        self.filetype(self.argv(n = 3))

        if self.filetype() == "raw" and self.argc() >= 6:
            self.fs(self.argv(n = 4))
            self.bit_depth(self.argv(n = 5))
        elif self.filetype() == "raw":
            raise Exception("Both sampling frequency and bit depth must be specified for RAW format.")

        if self.argc() == 7:
            if self.filename() is not None:
                self.blocksize(self.argv(n = 6))
            elif self.directory() is not None:
                self.freq_base(self.argv(n = 6))
            else:
                raise Exception("Unable to process command line argument 7")
        else:
            self.freq_base(997) # Default base frequency is 997

    def parse_op_calibrate(self):
        self.freq_base(self.argv(n = 2))
        self.cal_file(self.argv(n = 3))


    # Helpers

    def usage(self, argv):
        print("Usage:\n")
        print("\t%s analyze <file | directory> <type> [fs] [bit depth] [blocksize | base frequency]" % argv[0])
        print("\t%s meter <base frequency>" % argv[0])
        print("\t%s calibrate <base frequency> <cal file>" % argv[0])
        print("\t%s test <directory>" % argv[0])


