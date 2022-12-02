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


import numpy as np

from scipy.io import wavfile


class SWG():
    ### (S)ine (W)ave (G)enerator ###

    # Properties

    __init_args = None       # Original __init__ arguments
    __refresh = None         # Refresh generator

    __filename = None        # The output filename
    __ftype = None           # The output file type
    __fs = None              # Sampling frequency
    __freqs = None           # List of frequencies
    __amplitudes = None      # List of frequency amplitudes (in the same order as __freqs)
    __length = None          # Signal length (in seconds)


    # Initializers, Loaders and Reloaders

    def __init__(self, filename, ftype = "wav", fs = 48000, freqs = [ 997 ], amplitudes = [ 1. ], length = 2.):
        self.__init_args = [ filename, ftype, fs, freqs, amplitudes, length ]

        self.__refresh = self.load(*self.__init_args)

        try:
            self.refresh()
        except StopIteration:
            pass

    def load(self, filename, ftype = "wav", fs = 48000, freqs = [ 997 ], amplitudes = [ 1. ], length = 2.):
        self.filename(filename)

        if ftype != "wav":
            raise Exception("Unsupported file type: %s" % ftype)
        else:
            self.ftype(ftype)

        if type(fs) != int or fs < 0:
            raise Exception("Invalid sampling frequency: %s" % fs)
        else:
            self.fs(fs)

        if type(freqs) != list:
            raise Exception("Frequencies argument type must be a list.")
        else:
            self.freqs(freqs)

        if type(amplitudes) != list:
            raise Exception("Amplitudes argument type must be a list.")
        else:
            self.amplitudes(amplitudes)

        if length <= 0:
            raise Exception("Invalid length: %s" % length)
        else:
            self.length(length)

        while True:
            self._process()

            yield

    def reload(self):
        self.__refresh = \
            self.load(
                filename = self.filename(),
                ftype = self.ftype(),
                fs = self.fs(),
                freqs = self.freqs(),
                amplitudes = self.amplitudes(),
                length = self.length()
            )

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
    
    def filename(self, filename = None):
        if filename is not None:
            self.__filename = filename
            return self
        else:
            return self.__filename

    def ftype(self, ftype = None):
        if ftype is not None:
            self.__ftype = ftype
            return self
        else:
            return self.__ftype

    def fs(self, freq = None):
        if freq is not None:
            self.__fs = freq
            return self
        else:
            return self.__fs

    def freqs(self, freq_list = None):
        if freq_list is not None:
            self.__freqs = freq_list
            return self
        else:
            return self.__freqs

    def amplitudes(self, ampl_list = None):
        if ampl_list is not None:
            self.__amplitudes = ampl_list
            return self
        else:
            return self.__amplitudes

    def length(self, nr_secs = None):
        if nr_secs is not None:
            self.__length = nr_secs
            return self
        else:
            return self.__length


    # Processors and Pre-Processors
    
    def _process(self):
        self.io_write(self.signal_synth())


    # Synthesizers

    def signal_synth(self):
        samples = np.linspace(0, self.length(), int(self.fs() * self.length()), endpoint = False)

        sines = np.sin(2 * np.pi * self.freqs()[0] * samples) * self.amplitudes()[0]

        i = 1

        while i < len(self.freqs()):
            sines += np.sin(2 * np.pi * self.freqs()[i] * samples) * self.amplitudes()[i]
            i += 1

        return sines


    # I/O

    def io_write(self, signal):
        wavfile.write(self.filename(), self.fs(), signal.astype(np.float32))


