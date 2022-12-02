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

#
# import core interfaces
#
#  - Signal Data File (SDF)
#  - Time Domain Analyzer (TDA)
#  - Frequency Domain Analyzer (FDA)
#
from uaa_core import SDF, TDA, FDA

#
# import user interfaces
#
#  - User Interface Plotter (UIP)
#
from uaa_ui import UIP


try:
    _DEBUG_ENABLE
except NameError:
    _DEBUG_ENABLE = True


class AAA():
    ### (A)pplication: (A)udio (A)nalyzer ###

    # Properties

    __init_args = None        # Original __init__ arguments
    __refresh = None          # Refresh generator

    __cli = None              # CLI() object
    __dci = None              # DCI() object
    __freq_start = None       # Start frequency
    __freq_stop = None        # Stop frequency
    __freq_base = None        # Base frequency
    __xlog = None             # Set to True for x-axis logarithmic scale, otherwise False
    __sdf = None              # SDF() object
    __tda = None              # TDA() object
    __fda = None              # FDA() object
    __fda_multi = None        # list of FDA() objects (multi)
    __uip = None              # UIP() object
    __with_report_ui = None   # Graphical UI report (charts)
    __with_report_file = None # Text based report (csv, json, etc)
    __view_opts = []          # Visualization options (from config)


    # Initializers, Loaders and Reloaders

    def __init__(self, cli, dci, eqi, cci, freq_start = 20, freq_stop = None, xlog = True, with_report_ui = True, with_report_file = False):
        self.__init_args = [ cli, dci, eqi, cci, freq_start, freq_stop, xlog, with_report_ui, with_report_file ]

        self.__refresh = self.load(*self.__init_args)

        try:
            self.refresh()
        except StopIteration:
            pass

    def load(self, cli, dci, eqi, cci, freq_start = 20, freq_stop = None, xlog = True, with_report_ui = True, with_report_file = False):
        self.cli(cli)
        self.dci(dci)
        self.eqi(eqi)
        self.cci(cci)
        self.freq_start(freq_start)
        self.freq_stop(freq_stop)
        self.freq_base(self.cli().freq_base())
        self.xlog(xlog)
        self.with_report_ui(with_report_ui)
        self.with_report_file(with_report_file)
        self.view_opts(self.cci().config()["aaa"]["modes"][self.cci().config()["aaa"]["mode_default"]])

        self._process()

        while True:
            self._analyze()

            # Render the plot
            if _DEBUG_ENABLE: print("Rendering...")

            # If a blocksize was specified in the CLI, the UI should be
            # continuosly rendered based on the specified blocksize
            if self.cli().blocksize() is not None:
                self.uip().render(pause = (self.cli().blocksize() / self.cli().fs()))
                yield

                try:
                    self.fda().refresh() # Will also refresh dci, tda and sdf
                    self.uip().refresh()
                except StopIteration:
                    break
            else:
                if self.eqi().enabled() is True:
                    # If events are enabled, multiple rendering may occur,
                    # so we need a non-blocking interface
                    # ('single' must be False).
                    self.uip().render(single = False)
                else:
                    # If events are disabled, a single rendering is expected,
                    # so a blocking interface will suffice.
                    self.uip().render(single = True)
                    break

                # Get next event
                self.eqi().refresh()

                # Wait for events
                while self.eqi().triggered() is not True:
                    self.uip().pause(0.05)
                    self.eqi().refresh()
                    yield

                # Process event
                if self.eqi().type() == "event_freq_base":
                    if _DEBUG_ENABLE: print(" => EVENT => Freq Base: %s" % self.eqi().value())

                    self.cci().refresh()

                    self.freq_base(self.cci().freq_nearest(self.eqi().value()))

                    self.uip().refresh()
                elif self.eqi().type() == "event_view_mode":
                    if _DEBUG_ENABLE: print(" => EVENT => View Mode: %s" % self.eqi().value())

                    self.cci().refresh()

                    if self.eqi().value() < len(self.cci().config()["aaa"]["modes"]):
                        self.view_opts(self.cci().config()["aaa"]["modes"][self.eqi().value()])

                    self.uip().refresh()
                elif self.eqi().type() == "event_close":
                    if _DEBUG_ENABLE: print(" => EVENT => Close: %s" % self.eqi().value())

                    if self.eqi().value() is True:
                        break

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

    def dci(self, obj = None):
        if obj is not None:
            self.__dci = obj
            return self
        else:
            return self.__dci

    def eqi(self, obj = None):
        if obj is not None:
            self.__eqi = obj
            return self
        else:
            return self.__eqi

    def cci(self, obj = None):
        if obj is not None:
            self.__cci = obj
            return self
        else:
            return self.__cci

    def sdf(self, obj = None):
        if obj is not None:
            self.__sdf = obj
            return self
        else:
            return self.__sdf

    def tda(self, obj = None):
        if obj is not None:
            self.__tda = obj
            return self
        else:
            return self.__tda

    def fda(self, obj = None):
        if obj is not None:
            self.__fda = obj
            return self
        else:
            return self.__fda

    def fda_multi(self, obj_list = None, idx = None):
        if obj_list is not None:
            self.__fda_multi = obj_list
            return self
        elif idx is not None:
            return self.__fda_multi[idx]
        else:
            return self.__fda_multi

    def uip(self, obj = None):
        if obj is not None:
            self.__uip = obj
            return self
        else:
            return self.__uip

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

    def freq_base(self, freq = None):
        if freq is not None:
            self.__freq_base = freq
            return self
        else:
            return self.__freq_base

    def xlog(self, status = None):
        if status is not None:
            self.__xlog = status
            return self
        else:
            return self.__xlog

    def with_report_ui(self, status = None):
        if status is not None:
            self.__with_report_ui = status
            return self
        else:
            return self.__with_report_ui

    def with_report_file(self, status = None):
        if status is not None:
            self.__with_report_file = status
            return self
        else:
            return self.__with_report_file

    def view_opts(self, opts = None):
        if opts is not None:
            self.__view_opts = opts
            return self
        else:
            return self.__view_opts


    # Processors and Pre-Processors

    def _process(self, render = True):
        if self.cli().filename() is not None:
            # Disable events
            self.eqi().enabled(False)

            # Process input file
            if _DEBUG_ENABLE: print("Processing Signal Data File...")
            self.sdf(SDF(self.cli().filename(), ftype = self.cli().filetype(), fs = self.cli().fs(), bit_depth = self.cli().bit_depth(), blocksize = self.cli().blocksize()))

            # Process Time Domain
            if _DEBUG_ENABLE: print("Processing Time Domain Analyzer...")
            self.tda(TDA(self.sdf(), self.dci()))

            # Process Frequency Domain
            if _DEBUG_ENABLE: print("Processing Frequency Domain Analyzer...")
            self.fda(FDA(self.tda(), self.dci(), freq_start = self.freq_start(), freq_stop = self.freq_stop()))
        elif self.cli().directory() is not None:
            # Enable events
            self.eqi().enabled(True)

            # If the requested base frequency is not an exact match of a
            # test frequency, replace the requested value with the closest
            # frequency found in the test frequencies list.
            if self.freq_base() not in self.cci().config()["common"]["test_freqs"]:
                self.freq_base(self.cci().freq_nearest(self.freq_base()))

            fda_multi = []

            for f in self.cci().config()["common"]["test_freqs"]:
                if _DEBUG_ENABLE: print("Analyzing frequency: %d Hz" % f)

                sdf = SDF(self.cli().directory() + ("/l_%d.%s" % (f, self.cli().filetype())), ftype = self.cli().filetype(), fs = self.cli().fs(), bit_depth = self.cli().bit_depth())

                tda = TDA(sdf, self.dci(), periods = False if f != self.freq_base() else True)

                fda_multi.append(FDA(tda, self.dci(), freq_start = self.freq_start(), freq_stop = self.freq_stop()))

            self.fda_multi(fda_multi)
        else:
            raise Exception("No file or directory was specified to be processed.")

        # Process Plot
        if _DEBUG_ENABLE: print("Processing User Interface Plotter...")
        if render is True:
            self.uip(UIP(self.dci(), self.eqi()))

    def _analyze(self):
        if self.cli().filename() is not None:
            self._analyze_single()
        elif self.cli().directory() is not None:
            self._analyze_multi()
        else:
            raise Exception("No file or directory was specified to be analyzed.")

    def _analyze_single(self):
        if self.with_report_file() is True:
            self.report_file()

        if self.with_report_ui() is True:
            self.report_ui()

    def _analyze_multi(self):
        # Set the current FDA, SDF and TDA objects to be analyzed, based
        # on the selected base frequency.
        self.fda(self.fda_multi(idx = self.cci().config()["common"]["test_freqs"].index(self.freq_base())))
        self.sdf(self.fda().tda().sdf())
        self.tda(self.fda().tda())

        if not self.tda().periods():
            self.tda().reload() # Reload TDA to force period processing

        if self.with_report_file() is True:
            self.report_file(multi = True)

        if self.with_report_ui() is True:
            self.report_ui(multi = True)


    # Reporting

    def report_file(self, multi = False):
        raise Exception("Not implemented.")

    def report_ui(self, multi = False):
        # Peaks
        peaks = self.fda().peaks(20, pn_filter = True)

        # Worst Other
        wo = self.fda().worst_other(peaks = peaks, carrier = self.fda().ffreq())

        # Plot the measurements
        if "meas" in self.view_opts():
            measurements = {
                "Channels": (self.tda().channels(), ''),
                "Bit Depth": (self.tda().bit_depth() if self.tda().bit_depth() else "N/A", "bits" if self.tda().bit_depth() else ""),
                "FS": (self.tda().fs(), "Hz"),
                "Length": ("%.2f (%.2f)" % (self.tda().length(), self.tda().length_unpadded()), "secs"),
                "Carrier": ("%.2f" % self.fda().carrier(), "Hz"),
                "High / Low": ("%.1f / %.1f" % (self.fda().spectrum_magn_db().max(), self.fda().spectrum_magn_db().min()), self.dci().log_unit()),
                "Peak / RMS": ("%.3f / %.3f" % (self.fda().tda().vpeak(), self.fda().tda().vrms()), 'V'),
                "Noise Floor": ("%.2f" % self.fda().noise_floor(), self.dci().log_unit()),
                "PN@%dHz" % self.fda().pn()[0][0]: ("%.2f" % self.fda().pn()[0][1], "dBc/Hz"),
                "PN@%dHz" % self.fda().pn()[1][0]: ("%.2f" % self.fda().pn()[1][1], "dBc/Hz"),
                "PN@%dHz" % self.fda().pn()[2][0]: ("%.2f" % self.fda().pn()[2][1], "dBc/Hz"),
                "PN@%dHz" % self.fda().pn()[3][0]: ("%.2f" % self.fda().pn()[3][1], "dBc/Hz"),
                "THD+N (%)": ("%.8f" % self.fda().thdn(), '%'),
                "THD+N": ("%.2f" % self.fda().thdn(in_dB = True), 'dB'),
                "THD (%)": ("%.8f" % self.fda().thd(), '%'),
                "THD": ("%.2f" % self.fda().thd(in_dB = True), 'dB'),
                "SNR / SNRj": ("%.2f / %.2f" % (self.fda().snr(), self.fda().snr_jitter(self.fda().pn(), self.fda().ffreq())), "dB"),
                "SFDR": ("%.2f" % (self.fda().sfdr()), "dBc"),
                "ENOB": ("%.2f" % (self.fda().enob()), "bits"),
                "Jitter": ("%.8f" % (self.fda().jitter(self.fda().pn(), self.fda().ffreq()) * 10**9), "ns"),
                "WOF": ("%.3f" % wo[0], "Hz"),
                "WOP": ("%.2f" % wo[1], self.dci().log_unit()),
                "DC": ("%.2f" % self.fda().dc(), self.dci().log_unit()),
                "Freq. Res.": ("%.6f" % self.fda().freq_res(), "Hz")
            }

            if _DEBUG_ENABLE:
                print("count: %d, min: %d, avg: %.8f, max: %d" % self.tda().period_cmam())

                for k in measurements:
                    print("%s: %s %s" % (k, measurements[k][0], measurements[k][1]))

        # Plot FR, FFTNF, SFDR, THD, THD+N, SNR and RMS values on the chart
        if _DEBUG_ENABLE: print("Plotting metrics...")

        if multi is True:
            fr = []
            sfdr = []
            thd = []
            thdn = []
            snr = []

            for fda in self.fda_multi():
                fr.append(fda.spectrum_magn_db().max())
                sfdr.append(fda.spectrum_magn_db().max() - fda.sfdr())
                thd.append(fda.spectrum_magn_db().max() - fda.thd(in_dB = True))
                thdn.append(fda.spectrum_magn_db().max() - fda.thdn(in_dB = True))
                snr.append(fda.spectrum_magn_db().max() - fda.snr())

            x = self.cci().config()["common"]["test_freqs"]
        else:
            sfdr = [ self.fda().spectrum_magn_db().max() - self.fda().sfdr() ] * 2
            thd = [ self.fda().spectrum_magn_db().max() - self.fda().thd(in_dB = True) ] * 2
            thdn = [ self.fda().spectrum_magn_db().max() - self.fda().thdn(in_dB = True) ] * 2
            snr = [ self.fda().spectrum_magn_db().max() - self.fda().snr() ] * 2

            x = [ self.fda().freq_start(), self.fda().freq_stop() ]


        # Calculate plot limits

        if "fdm" in self.view_opts():
            pmin = 20 * (np.log10(self.fda().spectrum_magn_rms().min()) - 1)
            pmax = 20 * (np.abs(np.log10(self.fda().spectrum_magn_rms().min())) + 1)
        else:
            margin = 0.075
            pmin = np.inf if "fftnf" not in self.view_opts() else self.fda().noise_floor() + (self.fda().noise_floor() * (margin / 2.))
            pmax = -np.inf

            for k in self.view_opts():
                if k == "thd":
                    p = thd
                elif k == "thdn":
                    p = thdn
                elif k == "sfdr":
                    p = sfdr
                elif k == "snr":
                    p = snr
                elif multi is True and k == "fr":
                    p = fr
                else:
                    continue

                v = min(p) - abs((min(p) * margin))
                if v < pmin: pmin = v
                v = max(p) + abs((max(p) * margin))
                if v > pmax: pmax = v

        # Setup the plot

        self.uip().setup_xy_base()

        if "td" not in self.view_opts() and "vrms" not in self.view_opts():
            self.uip().setup_fd_xb1_yl1("Frequency (Hz)", "Magnitude (%s)" % self.dci().log_unit(), self.fda().freq_start(), self.fda().freq_stop(), pmin, pmax, xlog = self.xlog(), grid = False, minorticks = True, ynbins = 40 if "fdm" in self.view_opts() else 20)
        else:
            self.uip().setup_td_xb1_yl1("Time (s)", "Amplitude (V)", 0, 5. / self.fda().ffreq(), -np.ceil(self.tda().vpeak() * 2.85), np.ceil(self.tda().vpeak() * 2.85))

        self.uip().setup_fd_xt1_yr1("Frequency (Hz)", "Magnitude (%s)" % self.dci().log_unit(), self.fda().freq_start(), self.fda().freq_stop(), pmin, pmax, xlog = self.xlog(), ynbins = 40 if "fdm" in self.view_opts() else 20)

        if "fdp" in self.view_opts():
            self.uip().setup_sub_fdp(self.fda().freq_start(), self.fda().freq_stop())

        # Plots

        if "meas" in self.view_opts():
            self.uip().plot_measurements(measurements, 0.15, 0.955, yspacing = -0.05, kvspacing = 0.075, color = "yellow")
        if "peaks" in self.view_opts():
            self.uip().plot_peaks(peaks, 0.0125, -0.15, yspacing = -0.04, kvspacing = 0.015, color = "white", chart_peaks_count = 6)
        if "fr" in self.view_opts() and multi is True:
            self.uip().plot_test_metric(x, fr, color = "bisque", linestyle = "--", linewidth = 1.25, label = "FR")
        if "sfdr" in self.view_opts():
            self.uip().plot_test_metric(x, sfdr, color = "fuchsia", linestyle = ":", linewidth = 1, label = "SFDR")
        if "thd" in self.view_opts():
            self.uip().plot_test_metric(x, thd, color = "cyan", linestyle = ":", linewidth = 1, label = "THD")
        if "thdn" in self.view_opts():
            self.uip().plot_test_metric(x, thdn, color = "deeppink", linestyle = "--", linewidth = 0.5, label = "THD+N")
        if "snr" in self.view_opts():
            self.uip().plot_test_metric(x, snr, color = "green", linestyle = "--", linewidth = 1.75, label = "SNR")

        if "fftnf" in self.view_opts():
            self.uip().plot_test_metric(
                [ self.fda().freq_start(), self.fda().freq_stop() ],
                [ self.fda().noise_floor() ] * 2,
                color = "white", linestyle = ":", linewidth = 1.15,
                label = "FFTNF",
                delta = False
            )

        if "vrms" in self.view_opts():
            self.uip().plot_test_metric(
                [ 0, 5. / self.fda().ffreq() ],
                [ self.tda().vrms() ] * 2,
                color = "orange", linestyle = "-.", linewidth = 1.65,
                label = "Vrms",
                on_host = True,
                delta = False
            )

        # Plot the time domain
        if "td" in self.view_opts():
            if _DEBUG_ENABLE: print("Plotting time domain...")
            signal_plot_id = len(self.uip().plots())
            for w, t in self.tda().gen_waveform(n = 5, ffreq = self.fda().carrier(accuracy = 1)):
                self.uip().plot_signal(t, w / (self.tda().signal_n().max() / self.tda().vpeak()), color = "yellow", antialiased = True, plot_id = signal_plot_id)

        # Plot the frequency domain magnitude
        if "fdm" in self.view_opts():
            if _DEBUG_ENABLE: print("Plotting frequency domain magnitude...")
            self.uip().plot_spectrum_magn(
                self.fda().fft_trim(self.fda().spectrum_fftfreq(), self.fda().freq_start(), self.fda().freq_stop()),
                self.fda().fft_trim(self.fda().spectrum_magn_db(), self.fda().freq_start(), self.fda().freq_stop()),
                antialiased = False
            )

        # Plot the frequency domain phase
        if "fdp" in self.view_opts():
            if _DEBUG_ENABLE: print("Plotting frequency domain phase...")
            self.uip().plot_spectrum_phase(
                self.fda().fft_trim(self.fda().spectrum_fftfreq(), self.fda().freq_start(), self.fda().freq_stop()),
                self.fda().fft_trim(self.fda().spectrum_phase_n(), self.fda().freq_start(), self.fda().freq_stop()),
                antialiased = False
            )


