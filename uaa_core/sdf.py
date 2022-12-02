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
import soundfile as sf

from scipy.io import wavfile


class SDF():
    ### (S)ignal (D)ata (F)ile ###

    # Properties

    __init_args = None        # Original __init__ arguments
    __refresh = None          # Refresh generator

    __filename = None         # The signal data filename
    __fs = None               # Sampling Frequency
    __blocksize = None        # Number of frames to read per block
    __overlap = None          # Number of frames to rewind between each block
    __channels = None         # Number of Channels
    __length_unpadded = None  # The original length (unpadded, if padding occured) of the sound file in seconds
    __bit_depth = None        # Bit Depth
    __ftype = None            # The type of signal data file
    __fsubtype = None         # The subtype of the signal data file
    __mmap = None             # If True, use mmap() when loading file, if supported
    __average_channels = None # If True, average signal levels from all channels (reduce all channels to one, by averaging them)
    __signal = None           # Signal Data
    __normalized = None       # Indicates if the signal amplitude is normalized between [ -1., 1. ]


    # Initializers, Loaders and Reloaders

    def __init__(self, filename, fs = None, ftype = "raw", bit_depth = 0, fsubtype = None, channels = 1, mmap = False, average_channels = False, blocksize = None, overlap = 0):
        self.__init_args = [ filename, fs, ftype, bit_depth, fsubtype, channels, mmap, average_channels, blocksize, overlap ]

        self.__refresh = self.load(*self.__init_args)

        try:
            self.refresh()
        except StopIteration:
            pass

    def load(self, filename, fs = None, ftype = "raw", bit_depth = 0, fsubtype = None, channels = 1, mmap = False, average_channels = False, blocksize = None, overlap = 0):
        self.filename(filename)
        self.ftype(ftype)
        self.bit_depth(bit_depth)
        self.fsubtype(fsubtype)
        self.channels(channels)
        self.mmap(mmap)
        self.average_channels(average_channels)
        self.blocksize(blocksize)
        self.overlap(overlap)

        if ftype == 'wav':
            # Load WAV
            fs, signal = wavfile.read(filename, mmap = mmap)
        elif ftype == 'raw':
            # Load RAW
            if fs is None:
                raise Exception("No sampling frequency was specified for the RAW format.")

            if fsubtype is None and bit_depth:
                fsubtype = "PCM_%d" % bit_depth
            else:
                raise Exception("RAW format requires 'fsubtype' or 'bit_depth' to be provided.")

            if self.blocksize() is not None:
                signal = sf.blocks(filename, blocksize = blocksize, overlap = overlap, channels = channels, samplerate = fs, format = "RAW", subtype = fsubtype)
            else:
                signal, _ = sf.read(filename, channels = channels, samplerate = fs, format = "RAW", subtype = fsubtype)
        else:
            raise Exception("Unsupported file type: %s" % ftype)

        self.fs(fs)

        if blocksize is not None:
            for block in signal:
                self.signal(block)

                self._process()
                self._normalize(average_channels)

                yield
        else:
            self.signal(signal)

            self._process()
            self._normalize(average_channels)

    def reload(self):
        self.__refresh = \
            self.load(
                filename = self.filename(),
                fs = self.fs(),
                ftype = self.ftype(),
                bit_depth = self.bit_depth(),
                fsubtype = self.fsubtype(),
                channels = self.channels(),
                mmap = self.mmap(),
                average_channels = self.average_channels(),
                blocksize = self.blocksize(),
                overlap = self.overlap()
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
        try:
            next(self.__refresh)
        except StopIteration:
            if self.blocksize() is None: pass
            else: raise


    # Setters and Getters
    #
    # NOTE: The built-in decorator @property is not used here so all
    #       setters/getters defined in this file are consistent with other
    #       complex forms of setters/getters used throughout the rest
    #       of this project.
    #
    # NOTE: It is possible, however, that this might change to @property in
    #       the future.

    def filename(self, file:str = None):
        if file is not None:
            self.__filename = file
            return self
        else:
            return self.__filename

    def fs(self, freq = None):
        if freq is not None:
            self.__fs = freq
            return self
        else:
            return self.__fs

    def blocksize(self, count = None):
        if count is not None:
            self.__blocksize = count
            return self
        else:
            return self.__blocksize

    def overlap(self, n = None):
        if n is not None:
            self.__overlap = n
            return self
        else:
            return self.__overlap

    def channels(self, count = None):
        if count is not None:
            self.__channels = count
            return self
        else:
            return self.__channels

    def length_unpadded(self, nr_secs = None):
        if nr_secs is not None:
            self.__length_unpadded = nr_secs
            return self
        else:
            return self.__length_unpadded

    def bit_depth(self, nr_bits = None):
        if nr_bits is not None:
            self.__bit_depth = nr_bits
            return self
        else:
            return self.__bit_depth

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

    def mmap(self, status = None):
        if status is not None:
            self.__mmap = status
            return self
        else:
            return self.__mmap

    def average_channels(self, status = None):
        if status is not None:
            self.__average_channels = status
            return self
        else:
            return self.__average_channels

    def signal(self, data = None):
        if data is not None:
            self.__signal = data
            return self
        else:
            return self.__signal

    def normalized(self, status = None):
        if status is not None:
            self.__normalized = status
            return self
        else:
            return self.__normalized


    # Processors and Pre-Processors

    def _process(self):
        self.channels(1 if len(self.signal().shape) == 1 else self.signal().shape[1])
        self.length_unpadded(self.signal().shape[0] / float(self.fs()))

        data_T_elem_type = type(self.signal().T[0]) if self.channels() == 1 else type(self.signal().T[0][0])

        # Determine bit depth
        if data_T_elem_type == np.float32 or data_T_elem_type == np.float64:
            # NOTE: if the element type is float, make sure that it is normalized within [ -1., 1. ].

            if np.abs(self.signal().max()) > 1 or np.abs(self.signal().min()) > 1:
                speak = np.abs(self.signal().max()) if np.abs(self.signal().max()) > np.abs(self.signal().min()) else np.abs(self.signal().min())
                self.signal(self.signal() / speak)

            assert(1 >= self.signal().max() >= self.signal().min() >= -1)

            if not self.bit_depth():
                self.bit_depth(64 if data_T_elem_type == np.float64 else 32)

            self.normalized(True)
        elif data_T_elem_type == np.uint8:
            self.bit_depth(8)
        elif data_T_elem_type == np.int16:
            self.bit_depth(16)
        elif data_T_elem_type == np.int32:
            # scipy wav 24-bit handler shifts a value stored in a 32-bit by
            # 8 bits to the left, so if all 8 LSB of the max value are 0,
            # then the bit depth is 24-bit, and not 32-bit.
            if np.int32(self.signal().max() << 24) == 0:
                self.bit_depth(24)
            else:
                self.bit_depth(32)

        # If bit depth was set to zero, try to infer from the file subtype if the format is 'raw' (soundfile lib specific)
        if not self.bit_depth() and self.ftype() == 'raw' and self.fsubtype() is not None:
            if self.fsubtype() == "PCM_S8" or self.fsubtype() == "PCM_U8":
                self.bit_depth(8)
            elif self.fsubtype() == "PCM_16":
                self.bit_depth(16)
            elif self.fsubtype() == "PCM_24":
                self.bit_depth(24)
            elif self.fsubtype() == "PCM_32" or self.fsubtype() == "FLOAT":
                self.bit_depth(32)
            elif self.fsubtype() == "DOUBLE":
                self.bit_depth(64)

        # Make sure we have a bit_depth set
        if not self.bit_depth():
            raise Exception("Unable to determine bit depth and none was specified.")

    def _normalize(self, average_channels = False):
        # Fetch signal data
        signal_data = self.signal().T if self.channels() == 1 else self.signal().T[0]

        # Handle lib-specific nuisances
        if self.bit_depth() and not self.normalized():
            if self.bit_depth() == 24 and self.ftype() == 'wav':
                # Wav files are processed by scipy, which requires a 8bit
                # shift towards LSB for 24-bit depth.
                self.signal(np.right_shift(signal_data, 8))
        else:
            self.signal(signal_data)

        if not self.normalized():
            # Determine normalization [ -1., 1. ] based on bit depth.
            if self.bit_depth():
                self.signal(np.divide(self.signal(), 1 << (self.bit_depth() - 1)))
            else:
                # If no bit depth is specified, or it is 0, raise an
                # exception as we are unable to proceed.
                raise Exception("Unable to normalize the signal. Bit depth couldn't be determined.")

        # Average the amplitudes of all channels, if requested
        if average_channels is True and self.channels() > 1:
            self.signal(self.signal().mean(axis = 1))

        # Consider the signal level normalized from this point on
        self.normalized(True)


