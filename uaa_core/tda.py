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


class TDA():
    ### (T)ime (D)omain (A)nalyzer ###

    # Properties

    __init_args = None       # Original __init__ arguments
    __refresh = None         # Refresh generator

    __sdf = None             # Signal Data File
    __dci = None             # Device Calibration Interface
    __fs = None              # Sampling Frequency
    __channels = None        # Number of Channels
    __length_unpadded = None # The original length (unpadded, if padding occured) of the sound file in seconds
    __length = None          # The length of the sound file in seconds
    __bit_depth = None       # Bit Depth
    __signal = None          # Signal Data
    __signal_n = None        # Normalized signal data
    __signal_periods = None  # 2D array (i,j) of signal periods: each 'i' element represents 'j' signal_n indexes of a full period
    __rms = None             # RMS amplitude of the normalized signal
    __vrms = None            # RMS amplitude of the normalized signal divided by RMS calibration 
    __vpeak = None           # Peak amplitude of the normalized signal divided by RMS calibration 
    __period_cmam = None     # CMAM: Count, min, average, max
                             #       - the total, min, avg and max amount of samples found from all wave periods
    __periods = None         # Set to True if periods were processed. Otherwise, set to False.


    # Initializers, Loaders and Reloaders

    def __init__(self, sdf, dci = None, read = True, process = True, normalize = True, periods = True, pad2sec = None):
        self.__init_args = [ sdf, dci, read, process, normalize, periods, pad2sec ]

        self.__refresh = self.load(*self.__init_args)

        try:
            self.refresh()
        except StopIteration:
            pass

    def load(self, sdf, dci = None, read = True, process = True, normalize = True, periods = True, pad2sec = None):
        self.periods(periods)

        if normalize is True and dci is None:
            raise Exception("When 'normalize' is True, 'dci' must be provided.")

        while True:
            self.sdf(sdf)
            self.dci(dci)
            self.fs(sdf.fs())
            self.channels(sdf.channels())
            self.length_unpadded(sdf.length_unpadded())
            self.bit_depth(sdf.bit_depth())

            if read is True:
                if pad2sec is not None and self.signal().size < (self.fs() * pad2sec):
                    # Zero-pad the signal for a final length of 'pad2sec' seconds
                    self.signal(np.pad(self.signal(), (0, (self.fs() * pad2sec) - self.signal().size)))
                else:
                    self.signal(sdf.signal())
            else:
                raise Exception("Unsupported operation.")

            if process is True:
                self._process()

                if normalize is True:
                    self._normalize()
            elif normalize is True:
                raise Exception("Cannot normalize when 'process' is not `True`.")

            yield

            try:
                sdf.refresh()

                if dci is not None:
                    dci.refresh()
            except StopIteration:
                break

    def reload(self, periods = True, refresh = False):
        if refresh is True:
            self.sdf().refresh()

            if self.dci() is not None:
                self.dci().refresh()

        self.periods(periods)

        self.__refresh = self.load(self.sdf(), dci = self.dci(), periods = self.periods())

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

    def sdf(self, f = None):
        if f is not None:
            self.__sdf = f
            return self
        else:
            return self.__sdf

    def dci(self, c = None):
        if c is not None:
            self.__dci = c
            return self
        else:
            return self.__dci

    def fs(self, freq = None):
        if freq is not None:
            self.__fs = freq
            return self
        else:
            return self.__fs

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

    def length(self, nr_secs = None):
        if nr_secs is not None:
            self.__length = nr_secs
            return self
        else:
            return self.__length

    def bit_depth(self, nr_bits = None):
        if nr_bits is not None:
            self.__bit_depth = nr_bits
            return self
        else:
            return self.__bit_depth

    def signal(self, data = None):
        if data is not None:
            self.__signal = data
            return self
        else:
            return self.__signal

    def signal_n(self, data = None):
        if data is not None:
            self.__signal_n = data
            return self
        else:
            return self.__signal_n

    def signal_periods(self, periods = None):
        if periods is not None:
            self.__signal_periods = periods
            return self
        else:
            return self.__signal_periods

    def rms(self, rms = None):
        if rms is not None:
            self.__rms = rms
            return self
        else:
            return self.__rms

    def vrms(self, vrms = None):
        if vrms is not None:
            self.__vrms = vrms
            return self
        else:
            return self.__vrms

    def vpeak(self, vpeak = None):
        if vpeak is not None:
            self.__vpeak = vpeak
            return self
        else:
            return self.__vpeak

    def period_cmam(self, cmam = None):
        if cmam is not None:
            self.__period_cmam = cmam
            return self
        else:
            return self.__period_cmam

    def periods(self, status = None):
        if status is not None:
            self.__periods = status
            return self
        else:
            return self.__periods


    # Processors and Pre-Processors

    def _process(self):
        self.length(self.signal().shape[0] / float(self.fs()))

    def _normalize(self):
        # Signal amplitudes MUST be normalized to [ -1., 1. ]
        if not self.sdf().normalized():
            raise Exception("Source signal is not normalized between [ -1., 1. ].")

        assert(self.signal().min() >= -1 and self.signal().max() <= 1)

        self.signal_n(self.signal())

        # Calculate normalized RMS value
        self.rms(np.sqrt(np.sum(np.power(self.signal_n(), 2)) / self.signal_n().size))

        # Calculate RMS voltage
        self.vrms(self.rms() / self.dci().nrms())

        # Calculate peak voltage
        self.vpeak(self.signal_n().max() / self.dci().nrms())

        # Separate signal data into a set of single periods,
        # identified by start and end sample index each
        #
        # Requires numpy 1.23
        if self.periods() is True:
            self.signal_periods(np.fromiter(self.gen_period(), dtype = np.dtype((np.uint32, 2))))

            # Calculate the total, min, avg and max size (in samples) of
            # the entire set of periods.
            self.period_cmam(self.period_analyze())


    # Generators

    def gen_period(self, start = 0, end = -1):
        start_idx = start
        end_idx = None
        s = 1 + start_idx
        signal_len = self.signal_n().size
        half_min_res = (1. / (1 << (self.bit_depth() if self.bit_depth() else 32))) / 2.  # Half value of the minimum resolution
        # Any value below `half_min_res` shall be set to zero
        # as floating-point round-off error near zero crossings may
        # become a problem for correct near-zero-sample period allocation.
        #
        # Although round() would lead to a much cleaner implementation,
        # its performance would considerably degrade the speed here.

        while True:
            # Find a zero crossing from an ascending amplitude
            while s < (signal_len - 1):
                # Start index should point to the zero or first positive
                # sample at the start of the period.
                sn_prev = 0 if abs(self.signal_n()[s - 1]) < half_min_res else self.signal_n()[s - 1]
                sn_cur = 0 if abs(self.signal_n()[s]) < half_min_res else self.signal_n()[s]
                if sn_prev <= 0 and sn_cur > 0: break
                s += 1

            # Found the start of the period.
            # start_idx is the sample index that points to a zero or positive
            # value at the beginning of a period.
            sn_prev = 0 if abs(self.signal_n()[s - 1]) < half_min_res else self.signal_n()[s - 1]
            start_idx = (s - 1) if sn_prev == 0 else s

            # We are at the start of a period.
            zx = False
            s += 1
            while s < signal_len:
                if zx is False:
                    sn_cur = 0 if abs(self.signal_n()[s]) < half_min_res else self.signal_n()[s]
                    if sn_cur <= 0: zx = True # Zero crossing detected
                else:
                    sn_cur = 0 if abs(self.signal_n()[s]) < half_min_res else self.signal_n()[s]
                    if sn_cur >= 0: break

                s += 1

            if end != -1 and s > end: break

            # Validate if we have a full period - if not, break the generator
            try:
                sn_cur = 0 if abs(self.signal_n()[s]) < half_min_res else self.signal_n()[s]
                if zx is False or sn_cur < 0: break
            except: break

            # Found the end of the period.
            # end_idx is the sample index that points to the last negative
            # value at the end of a period (always less than zero value)
            end_idx = s - 1

            yield start_idx, end_idx

    def gen_waveform(self, n = 1, ffreq = None):
        count = 1
        start_idx = self.signal_periods()[0][0]

        if ffreq is None:
            ffreq = self.ffreq_infer()

        for si, ei in self.signal_periods():
            if count < n:
                count += 1
                continue

            # Fetch waveform from period interval
            w = self.signal_n()[start_idx:ei + 1]

            # Craft a linear spaced array to represent and match the time of waveform
            t = np.linspace(0, len(w) / self.fs(), len(w), endpoint = False)

            # Compensate the time array by:
            #
            #  - Adding the time offset of the starting period sample number
            #    (start_idx)
            #
            #  - Subtracting the time offset of the sample number from where
            #    the first valid period of the waveform begins
            #    (self.signal_periods()[0][0])
            t += \
                ((start_idx % (1. / (ffreq / self.fs()))) * (1. / self.fs())) - \
                ((self.signal_periods()[0][0] % (1. / (ffreq / self.fs()))) * (1. / self.fs()))

            yield w, t

            count = 1
            start_idx = ei + 1


    # Calculators

    def period_analyze(self):
        # We add 1 to end_idx, given that end_idx points to the last sample
        # of the detected period, and NOT the first sample of the next period
        pr = np.add(1, np.diff(self.signal_periods()))

        return (pr.size, pr.min(), np.sum(pr) / pr.size, pr.max())

    def period_infer(self):
        # Infer period - return the average _number of samples_ per period
        # (how many samples in a period, on average)
        return self.period_cmam()[2]

    def ffreq_infer(self, round_to = 1):
        # Infer fundamental frequency from period. The period is defined here
        # as the number of samples per period, not in seconds.
        return np.round(self.fs() / self.period_infer(), round_to)


