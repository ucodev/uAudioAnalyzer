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

from scipy.fftpack import fft,fftfreq


class FDA():
    ### (F)requency (D)omain (A)nalyzer ###

    # Properties

    __init_args = None           # Original __init__ arguments
    __refresh = None             # Refresh generator

    __tda = None                 # Time-Domain Signal data
    __dci = None                 # Device Calibration Interface
    __spectrum_fft = None        # Spectrum Data from Signal
    __spectrum_magn = None       # Magnitudes from complex FFT result 
    __spectrum_phase = None      # Phase angles from complex FFT result
    __spectrum_fftfreq = None    # Bins from sampling frequency
    __spectrum_magn_n = None     # Normalized magnitudes [ 0., 1. ]
    __spectrum_phase_n = None    # Normalized phase angles [ -1., 1. ], representing a multiple of np.pi
    __spectrum_magn_rms = None   # Normalized spectrum as RMS of __spectrum_magn_n
    __spectrum_magn_db = None    # Spectrum data in dB
    __ffreq = None               # Fundamental Frequency
    __pn_list = None             # Phase Noise
    __h_idxs_list = None         # List of Harmonics indexes

    N1D76 = None                 # See __init__() and/or load()
    N6D02 = None                 # See __init__() and/or load()


    # Initializers, Loaders and Reloaders

    def __init__(self, tda, dci, process = True, normalize = True, analyze = True, freq_start = None, freq_stop = None):
        self.__init_args = [ tda, dci, process, normalize, analyze, freq_start, freq_stop ]

        self.__refresh = self.load(*self.__init_args)

        try:
            self.refresh()
        except StopIteration:
            pass

    def load(self, tda, dci, process = True, normalize = True, analyze = True, freq_start = None, freq_stop = None):
        self.N1D76 = 10 * np.log10(3. / 2) # See: Analog Devices MT-229, Equation 11
        self.N6D02 = 20 * np.log10(2)      # See: Analog Devices MT-229, Equation 11

        if freq_start is None:
            freq_start = 0

        if freq_stop is None:
            freq_stop = tda.fs() / 2

        self.freq_start(freq_start)
        self.freq_stop(freq_stop)

        while True:
            self.tda(tda)
            self.dci(dci)

            if process is True:
                self._process()

                if normalize is True:
                    self._normalize()

                    if analyze is True:
                        self._analyze()
                elif analyze is True:
                    raise Exception("Cannot analyze when 'normalize' is not `True`.")
            elif normalize is True:
                raise Exception("Cannot normalize when 'process' is not `True`.")

            yield

            try:
                tda.refresh()
                dci.refresh()
            except StopIteration:
                break

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

    def tda(self, a = None):
        if a is not None:
            self.__tda = a
            return self
        else:
            return self.__tda

    def dci(self, c = None):
        if c is not None:
            self.__dci = c
            return self
        else:
            return self.__dci

    def freq_start(self, freq = None):
        if freq is not None:
            self.__freq_start = freq
            return self
        else:
            return self.__freq_start

    def freq_stop(self, freq = None):
        if freq is not None:
            self.__freq_stop = freq
            return self
        else:
            return self.__freq_stop

    def spectrum_fft(self, fft = None):
        if fft is not None:
            self.__spectrum_fft = fft
            return self
        else:
            return self.__spectrum_fft

    def spectrum_magn(self, abs_fft = None):
        if abs_fft is not None:
            self.__spectrum_magn = abs_fft
            return self
        else:
            return self.__spectrum_magn

    def spectrum_phase(self, angle_fft = None):
        if angle_fft is not None:
            self.__spectrum_phase = angle_fft
            return self
        else:
            return self.__spectrum_phase

    def spectrum_fftfreq(self, fftfreq = None):
        if fftfreq is not None:
            self.__spectrum_fftfreq = fftfreq
            return self
        else:
            return self.__spectrum_fftfreq

    def spectrum_magn_n(self, fft_norm_magn = None):
        if fft_norm_magn is not None:
            self.__spectrum_magn_n = fft_norm_magn
            return self
        else:
            return self.__spectrum_magn_n

    def spectrum_phase_n(self, fft_norm_angle = None):
        if fft_norm_angle is not None:
            self.__spectrum_phase_n = fft_norm_angle
            return self
        else:
            return self.__spectrum_phase_n

    def spectrum_magn_rms(self, fft_rms = None):
        if fft_rms is not None:
            self.__spectrum_magn_rms = fft_rms
            return self
        else:
            return self.__spectrum_magn_rms

    def spectrum_magn_db(self, fft_db = None):
        if fft_db is not None:
            self.__spectrum_magn_db = fft_db
            return self
        else:
            return self.__spectrum_magn_db

    def ffreq(self, freq = None):
        if freq is not None:
            self.__ffreq = freq
            return self
        else:
            return self.__ffreq

    def pn(self, pn_list = None):
        if pn_list is not None:
            self.__pn_list = pn_list
            return self
        else:
            return self.__pn_list

    def h_idxs(self, h_idxs_list = None, n = 10):
        if h_idxs_list is not None:
            self.__h_idxs_list = h_idxs_list
            return self
        else:
            if n > len(self.__h_idxs_list): n = len(self.__h_idxs_list)

            return self.__h_idxs_list[0:n]


    # Processors and Pre-Processors

    def _process(self):
        signal = self.tda().signal_n()

        self.spectrum_fft(fft(signal))
        self.spectrum_fftfreq(fftfreq(signal.size, 1. / self.tda().fs()))

    def _normalize(self):
        # Normalize spectral data

        # Take the polar magnitudes from the rectangular complex FFT result.
        # This is achieved by np.abs(complex)
        self.spectrum_magn(np.abs(self.spectrum_fft())[0:self.spectrum_fft().size // 2])

        # Take the polar phase angle from the rectangular complex FFT result.
        # This is achieved by np.angle(complex)
        self.spectrum_phase(np.angle(self.spectrum_fft())[0:self.spectrum_fft().size // 2])

        # Normalize magnitudes [ 0., 1. ]
        self.spectrum_magn_n(np.divide(self.spectrum_magn(), self.spectrum_magn().size))
        self.spectrum_magn_rms(np.multiply(self.tda().rms() / self.tda().signal_n().max(), self.spectrum_magn_n()))
        self.spectrum_magn_db(
            np.add(np.multiply(10, # Multiply by 10x as we are dealing with power, given that the magnitude is being squared below
                np.log10(
                    np.divide(np.power(np.divide(self.spectrum_magn_rms(), self.dci().nrms()), 2), self.dci().impedance())
                            # ^^^^^^^^^ Squared magnitude                                     ^^^
                )
            ), self.dci().log_offset())
        )

        # Normalize phase angles [ -1., 1. ], representing the range of
        # [ -1*pi, 1*pi ]
        self.spectrum_phase_n(np.divide(self.spectrum_phase(), np.pi))

        # Set the fundamental frequency
        self.ffreq(self.spectrum_fftfreq()[np.argmax(self.spectrum_magn_n()[1:]) + 1]) # Excluded DC

        # Get the first 'n' harmonics, taking aliasing into account
        self.h_idxs(np.array(list(map(lambda f: self.freq2idx(f), self.gen_harmonics_freq(20)))))

    def _analyze(self):
        # Phase noise
        #
        # TODO: include offsets up to (2*self.ffreq()-1) and use negative
        #       offsets if (2*self.ffreq()-1) > (self.td_source().fs() / 2)
        #       ... also avoid choosing offsets that match harmonics
        offsets = []
        pn = []

        # The first offset calculation must take into account the spectrum
        # resolution to avoid including the carrier magnitude into the
        # theoretical range [-0.5, 0.5], that can in practice be overshot
        # due to the lack of spectrum resolution
        offsets.append(int(np.ceil(self.freq_res() * 2)))
        offsets.append(offsets[0] * 2 if offsets[0] >= 10 else 10)
        offsets.append(offsets[1] * 2 if offsets[1] >= 110 else 100)
        offsets.append(offsets[2] * 2 if offsets[2] >= 1100 else 1000)

        for o in offsets:
            pn.append((o, self.phase_noise(o)))

        self.pn(pn)


    # Filters


    # Generators

    def gen_harmonics_freq(self, n = 10):
        # Generates the frequency value for the harmonics of the fundamental
        # frequency, including aliasing
        #
        # See: Analog Devices MT-003, Figure 3

        Nn = n + 1
        Kn = int(np.ceil(Nn / (self.tda().fs() / self.ffreq())))

        harmonics_freqs = []

        for K in range(0, Kn + 1):
            for N in range(0, Nn + 1):
                h = abs((K * self.tda().fs()) - (N * self.ffreq()))

                if h == 0 or h >= (self.tda().fs() / 2) or (h in harmonics_freqs) or h == self.ffreq():
                    continue

                harmonics_freqs.append(h)

                yield h


    # Converters

    def idx2freq(self, idx = None):
        if not idx:
            return None

        return idx / self.tda().length()

    def freq2idx(self, freq = None):
        if freq is None:
            return None

        return int(freq * self.tda().length())

    def freq2magn(self, freq, mtype = "rms"):
        if mtype == "rms":
            return self.spectrum_magn_rms()[self.freq2idx(freq)]
        elif mtype == "n":
            return self.spectrum_magn_n()[self.freq2idx(freq)]
        elif mtype == "dB":
            return self.spectrum_magn_db()[self.freq2idx(freq)]
        else:
            raise Exception("Invalid mtype supplied to freq2magn(): %s" % mtype)

    def freq2phase(self, freq):
        return self.spectrum_phase_n()[self.freq2idx(freq)]

    def fft_trim(self, fft_array, freq_start = 0, freq_stop = None):
        return fft_array[self.freq2idx(freq_start):self.freq2idx(freq_stop)]


    # Extractors

    def S(self, in_dB = False):
        # (S)ignal

        # See: Analog Devices MT-053, Figure 1

        if in_dB is True:
            return self.spectrum_magn_db()[1:].max()
        else:
            return self.spectrum_magn_rms()[1:].max()

    def D(self, n = 10, no_sqrt = False, freq_start = None, freq_stop = None):
        # (D)istortion

        if freq_start is None:
            freq_start = self.freq_start()

        if freq_stop is None:
            freq_stop = self.freq_stop()

        harmonics = []

        for h in self.h_idxs(n = n):
            if self.idx2freq(h) < freq_start or self.idx2freq(h) > freq_stop:
                continue

            harmonics.append(h)

        # If there are no harmonics to process in the supplied range, distortion is 0
        if not harmonics:
            return 0.

        # See: Analog Devices MT-053, Figure 1
        ret = np.sum(np.square(self.spectrum_magn_rms()[harmonics]))

        if no_sqrt is True:
            return ret

        return np.sqrt(ret)

    def N(self, n = 10, no_sqrt = False, freq_start = None, freq_stop = None):
        # (N)oise

        if freq_start is None:
            freq_start = self.freq_start()

        if freq_stop is None:
            freq_stop = self.freq_stop()

        # See: Analog Devices MT-053, Figure 1
        noise = np.ma.array(self.spectrum_magn_rms(), mask = False)

        # Mask DC
        noise.mask[0] = True
        # Mask Signal
        noise.mask[self.spectrum_magn_rms()[1:].argmax() + 1] = True
        # Mask Harmonics
        noise.mask[self.h_idxs(n = n)] = True

        ret = np.sum(np.square(self.fft_trim(noise, freq_start, freq_stop)))

        if no_sqrt is True:
            return ret

        return np.sqrt(ret)


    # Calculators

    def freq_res(self):
        # Returns the spectrum resolution, in Hz
        return 1. / self.tda().length_unpadded()

    def carrier(self, accuracy = 1.0):
        # Get the carrier frequency, with an accuracy of at least
        # 'accuracy' Hertz (default is 1.0 Hz)

        # If the spectrum resolution is lower than 'accuracy', then the
        # return value of self.ffreq() will suffice...
        if self.freq_res() <= accuracy:
            return self.ffreq()

        # ... otherwise, we need to pad the original signal with enough
        # zeros to increase its length to at least 'FS * (1. / accuracy)'
        signal_padded = np.pad(self.tda().signal_n(), (0, int(self.tda().fs() * np.ceil(1. / accuracy)) - self.tda().signal_n().size))

        # ... and take the FFT of the padded signal - now with enough
        # resolution to grant the requested accuracy
        s = fft(signal_padded)

        # Extract the carrier frequency from the FFT bin with the highest magnitude
        return (np.abs(s[1:s.size // 2]).argmax() + 1) / (signal_padded.size / self.tda().fs())

    def thdn(self, n = 10, in_dB = False, freq_start = None, freq_stop = None):
        # See: Analog Devices MT-003, Equation 5
        # See: Analog Devices MT-053, Figure 1

        if freq_start is None:
            freq_start = self.freq_start()

        if freq_stop is None:
            freq_stop = self.freq_stop()

        if in_dB is True:
            return 20 * np.log10((self.S() / (np.sqrt(self.N(n = n, no_sqrt = True) + self.D(n = n, no_sqrt = True)))))
        else:
            return 100. * (np.sqrt(self.N(n = n, no_sqrt = True, freq_start = freq_start, freq_stop = freq_stop) + self.D(n = n, no_sqrt = True, freq_start = freq_start, freq_stop = freq_stop)) / self.S())

    def thd(self, n = 10, in_dB = False, freq_start = None, freq_stop = None):
        # See: Analog Devices MT-003, Equation 4
        # See: Analog Devices MT-053, Figure 1

        # Get the first N harmonics (not the peaks as they can be
        # uncorrelated for this calculation)
        #
        # Default: first 10 harmonics
        #
        # Reason: By using the first 10 harmonics, the first 5 even and 5
        # odd harmonics are always included, allowing signals that are
        # mainly composed of second order harmonics and signals that are
        # mainly composed of or third order harmonics to be similarly
        # weighted by their first 5 dominant distortion products.
        #

        if freq_start is None:
            freq_start = self.freq_start()

        if freq_stop is None:
            freq_stop = self.freq_stop()

        if in_dB is True:
            return 20 * np.log10(self.S() / self.D(n = n, freq_start = freq_start, freq_stop = freq_stop))
        else:
            return 100. * (self.D(n = n, freq_start = freq_start, freq_stop = freq_stop) / self.S())

    def snr(self, n = 10, freq_start = None, freq_stop = None):
        # See: Analog Devices MT-003, Equation 13

        if freq_start is None:
            freq_start = self.freq_start()

        if freq_stop is None:
            freq_stop = self.freq_stop()

        return 20 * np.log10(self.S() / self.N(n = n, freq_start = freq_start, freq_stop = freq_stop))

    def snr_jitter(self, pn, fc):
        # See: MAXIM AN4466, Page 3
        # See: Texas Instruments TIPL 4704, Slide 4

        return -20 * np.log10(2 * np.pi * fc * self.jitter(pn, fc))

    def enob(self, freq_start = None, freq_stop = None):
        # See: Analog Devices MT-003, Equation 2

        if freq_start is None:
            freq_start = self.freq_start()

        if freq_stop is None:
            freq_stop = self.freq_stop()

        return ((self.thdn(in_dB = True, freq_start = freq_start, freq_stop = freq_stop) - self.N1D76) + (20 * np.log10(self.dci().nfullscale() / self.tda().rms()))) / self.N6D02

    def worst_other(self, peaks = None, harmonics = None, carrier = None, freq_start = None, freq_stop = None):
        if freq_start is None:
            freq_start = self.freq_start()

        if freq_stop is None:
            freq_stop = self.freq_stop()

        if peaks is None:
            peaks = self.peaks(pn_filter = True, freq_start = freq_start, freq_stop = freq_stop)

        if harmonics is None:
            # No need to filter harmonics in the range [ freq_start, freq_stop ],
            # as 'peaks' is already contained in that range, so any harmonics
            # from the following list that are outside of [ freq_start, freq_stop ]
            # range will be ignored when 'peaks' is iterated in the 'wo' loop below.
            harmonics = list(self.gen_harmonics_freq(n = 10))

        if carrier is None:
            carrier = self.carrier()

        # [ freq, magnitude, index ]
        wo = [ 0, -np.inf, 0 ]

        for p in peaks:
            if p[0] in harmonics or p[0] == carrier:
                continue

            if p[1] > wo[1]:
                wo = p

        return wo

    def peaks(self, n = 10, pn_filter = False, track_n = 64, freq_start = None, freq_stop = None):
        plist = []

        if freq_start is None:
            freq_start = self.freq_start()

        if freq_stop is None:
            freq_stop = self.freq_stop()

        harmonics = list(self.gen_harmonics_freq(n = n))

        sdb = np.copy(self.spectrum_magn_db())

        count = 0

        while count < n:
            idx = sdb.argmax()

            if idx == 0: # Exclude DC
                sdb[idx] = -np.inf
                continue

            # Only include the requested frequency range
            if self.spectrum_fftfreq()[idx] < freq_start or self.spectrum_fftfreq()[idx] > freq_stop:
                sdb[idx] = -np.inf
                continue

            # (freq, magnitude, index, is_harmonic, is_harmonic_even)
            freq = self.spectrum_fftfreq()[idx]
            plist.append((freq, sdb[idx], idx, freq in harmonics, (freq / self.carrier()) % 2 == 0))

            # Unlikely to happen, but make sure that we are not including
            # anything that isn't supposed to in the 'plist'
            assert(plist[-1][0] != -np.inf)

            sdb[idx] = -np.inf

            count += 1

            if pn_filter is not True:
                continue

            # Right-side Processing: Ignore phase noise to the right
            idx_offset = 1
            prev = np.array([ sdb[idx] ] * track_n) # Keep track of the last N points

            while (idx + idx_offset) > 0 and (idx + idx_offset) < (sdb.size - 1) and (sdb[idx + idx_offset] >= sdb[idx + idx_offset + 1] or sdb[idx + idx_offset + 1] <= prev.max()):
                prev = np.insert(prev[:-1], 0, sdb[idx + idx_offset])
                sdb[idx + idx_offset] = -np.inf
                idx_offset += 1

            # Left-side Processing: Ignore phase noise to the left
            idx_offset = -1
            prev = np.array([ sdb[idx] ] * track_n) # Keep track of the last N points

            while (idx + idx_offset) > 0 and (idx + idx_offset) < (sdb.size - 1) and (sdb[idx + idx_offset] >= sdb[idx + idx_offset - 1] or sdb[idx + idx_offset - 1] <= prev.max()):
                prev = np.insert(prev[:-1], 0, sdb[idx + idx_offset])
                sdb[idx + idx_offset] = -np.inf
                idx_offset -= 1

        return plist

    def phase_noise(self, offset, carrier = None):
        # See: Analog Devices MT-008, Figure 1

        if carrier is None:
            carrier = self.ffreq()

        # Get the minimum spectrum resolution (how many hertz from one
        # index to the next)
        idx_res = self.freq_res()

        # Ideally, 1Hz range, centered at the supplied carrier offset -
        # but the effective range will most likely differ
        idx_start = self.freq2idx(carrier + offset) - int(np.ceil(0.5 / idx_res))
        idx_stop = self.freq2idx(carrier + offset) + int(np.ceil(0.5 / idx_res))

        # Calculate the _effective_ frequency range that was selected
        # The effective range will most likely differ from [-0.5, 0.5] (1Hz).
        hz_range = (idx_stop - idx_start) * idx_res

        assert(hz_range >= 1)

        # hz_range will always be >= 1, so...
        #
        # If the frequency range (hz_range) is exactly 1 Hz:
        #   - The RSS is taken from the interval [the sum is divided by 1
        #     (given that hz_range == 1) before the square root], which is
        #     consistent with the standard noise calculation (RSS of the
        #     RMS magnitudes of all noise elements over an interval)
        #
        # If the frequency range (hz_range) is greater than 1 Hz:
        #   - The sum of squares of the RMS magnitudes is taken from the
        #     interval and divided by 'hz_range' so the value is scaled
        #     to represent a 1 Hz range. Then the square root is taken
        #     from the result to complete the RSS over the 1Hz range.
        #
        # The following calculation will cause 'dbc_hz' to reflect the
        # Phase Noise Power below the carrier per exactly 1 Hz (dBc/Hz)
        offset_norm_magn = np.sqrt(np.sum(np.square(self.spectrum_magn_rms()[idx_start:idx_stop])) / hz_range)

        # Get the carrier magnitude
        ffreq_magn = self.freq2magn(carrier)

        # Calculate the phase noise at this particular 'offset'
        dbc_hz = (20 * np.log10(ffreq_magn)) - (20 * np.log10(offset_norm_magn))

        return -dbc_hz

    def process_gain(self):
        # See: Analog Devices MT-003, Figure 2
        return 10 * np.log10((self.tda().fs() * self.tda().length()) / 2.)

    def noise_floor(self, center = None, span = None, freq_start = None, freq_stop = None):
        # See: Analog Devices MT-001, Figure 6
        # See: Analog Devices MT-003, Figure 2

        if freq_start is None:
            freq_start = self.freq_start()

        if freq_stop is None:
            freq_stop = self.freq_stop()

        # -(SNR measured) - (FFT process gain) + (carrier magnitude in dB)
        return -self.snr(freq_start = freq_start, freq_stop = freq_stop) - self.process_gain() + self.S(in_dB = True)

    def sfdr(self, freq_start = None, freq_stop = None):
        # See: Analog Devices MT-003, Figure 4
        # See: Analog Devices MT-053, Figure 6

        if freq_start is None:
            freq_start = self.freq_start()

        if freq_stop is None:
            freq_stop = self.freq_stop()

        p = self.peaks(2, pn_filter = True, freq_start = freq_start, freq_stop = freq_stop)

        return -(p[1][1] - p[0][1])

    def dc(self):
        return self.spectrum_magn_db()[0]

    def jitter(self, pn, fc):
        # See: MAXIM AN3359
        # See: Analog Devices, MT-008

        def f(i):
            # Frequency is index 0 of 'pn' element 'i'
            return pn[i][0]

        def Lf(i):
            # PN@f is index 1 of 'pn' element 'i'
            return pn[i][1]

        def a(i):
            # See: MAXIM AN3359, Equation 17
            return (Lf(i + 1) - Lf(i)) / (np.log10(f(i + 1)) - np.log10(f(i)))

        def b(i):
            # See: MAXIM AN3359, Equation 17
            return Lf(i)

        # See: MAXIM AN3359, Equation 16
        K = len(pn)
        rsum = 0
        i = 0

        while i < (K - 1):
            rsum += (10 ** (b(i) / 10.)) * (f(i) ** (-a(i) / 10.)) * ((a(i) / 10. + 1) ** -1) * ((f(i + 1) ** (a(i) / 10. + 1)) - (f(i) ** (a(i) / 10. + 1)))

            i += 1

        return np.sqrt(2 * rsum) / (2 * np.pi * fc)


