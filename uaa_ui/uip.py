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

import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter


class UIP():
    ### (U)ser (I)nterface (P)lotter ###

    # Properties

    __init_args = None  # Original __init__ arguments
    __refresh = None    # Refresh generator

    __dci = None        # Device Calibration Interface
    __eqi = None        # Event Handler Interface
    __fig = None        # figure layer
    __host = None       # host layer
    __pars = []         # parameter layers
    __subs = []         # subplot layers
    __plots = []        # list of plots
    __ylims = None      # y-axis limits
    __xlims = None      # x-axis limits


    # Initializers, Loaders and Reloaders

    def __init__(self, dci, eqi, xd = 14, yd = 8, parN = 2):
        self.__init_args = [ dci, eqi, xd, yd, parN ]

        self.__refresh = self.load(*self.__init_args)

        try:
            self.refresh()
        except StopIteration:
            pass

    def load(self, dci, eqi, xd = 14, yd = 8, parN = 2, subN = 1, subs_params = [ 919 ], subs_sharex = [ 1 ], subs_sharey = [ None ]):
        plt.rcParams['lines.color'] = "white"
        plt.rcParams['legend.labelcolor'] = "white"
        plt.rcParams['axes.labelcolor'] = "white"
        plt.rcParams['xtick.color'] = "white"
        plt.rcParams['ytick.color'] = "white"
        plt.rcParams['legend.facecolor'] = "black"

        fig, host = plt.subplots(figsize = (xd, yd))

        self.fig(fig)
        self.host(host)

        self.fig().canvas.mpl_connect('button_press_event', self.event_button_press)
        self.fig().canvas.mpl_connect('key_press_event', self.event_key_press)
        self.fig().canvas.mpl_connect('close_event', self.event_close)

        self.fig().patch.set_facecolor("black")
        self.host().patch.set_facecolor("black")

        for i in range(0, parN):
            self.pars(i, self.host().twinx().twiny())

        for i in range(0, subN):
            self.subs(i,
                self.fig().add_subplot(
                    subs_params[i],
                    facecolor = "none",
                    sharex = self.pars(subs_sharex[i]) if subs_sharex[i] is not None and subs_sharex[i] >= 0 else None if subs_sharex[i] is None else self.host(),
                    sharey = self.pars(subs_sharey[i]) if subs_sharey[i] is not None and subs_sharey[i] >= 0 else None if subs_sharey[i] is None else self.host()
                )
            )

            self.subs(i).tick_params(direction = "in", axis = "both", right = False, labelright = False, left = False, labelleft = False, bottom = False, labelbottom = False, top = False, labeltop = False, reset = True)

            for sp in self.subs(i).spines.values():
                sp.set_edgecolor("none")

            self.subs(i).get_xaxis().set_visible(False)
            self.subs(i).get_yaxis().set_visible(False)

        while True:
            self.dci(dci)
            self.eqi(eqi)

            yield

            try:
                dci.refresh()
            except StopIteration:
                break

            self.host().set_xscale("linear")
            self.host().clear()
            self.host().patch.set_facecolor("black")

            for i in range(0, parN):
                self.pars(i).set_xscale("linear")
                self.pars(i).clear()

            for i in range(0, subN):
                self.subs(i).set_xscale("linear")

                self.subs(i).get_xaxis().set_visible(False)
                self.subs(i).get_yaxis().set_visible(False)

                self.subs(i).tick_params(direction = "in", axis = "both", right = False, labelright = False, left = False, labelleft = False, bottom = False, labelbottom = False, top = False, labeltop = False, reset = True)
                for sp in self.subs(i).spines.values():
                    sp.set_edgecolor("none")

                self.subs(i).clear()

            self.plots(reset = True)

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

    def fig(self, pfig = None):
        if pfig is not None:
            self.__fig = pfig
            return self
        else:
            return self.__fig

    def host(self, phost = None):
        if phost is not None:
            self.__host = phost
            return self
        else:
            return self.__host

    def pars(self, idx = None, par = None, reset = False):
        if reset is True:
            self.__pars = []

        if idx is None:
            return self.__pars
        elif idx == len(self.__pars):
            self.__pars.append(None)
        elif idx > len(self.__pars):
            raise Exception("Non-continuos index requested in `pars` list")

        if par is not None:
            self.__pars[idx] = par
            return self
        else:
            return self.__pars[idx]

    def subs(self, idx = None, sub = None, reset = False):
        if reset is True:
            self.__subs = []

        if idx is None:
            return self.__subs
        elif idx == len(self.__subs):
            self.__subs.append(None)
        elif idx > len(self.__subs):
            raise Exception("Non-continuos index requested in `subs` list")

        if sub is not None:
            self.__subs[idx] = sub
            return self
        else:
            return self.__subs[idx]

    def plots(self, idx = None, p = None, reset = False):
        if reset is True:
            self.__plots = []

        if idx == None:
            return self.__plots
        elif idx == len(self.__plots):
            self.__plots.append(None)
        elif idx > len(self.__plots):
            raise Exception("Non-continuos index requested in `plots` list")

        if p is not None:
            self.__plots[idx] = p
            return self
        else:
            return self.__plots[idx]

    def ylims(self, lims = None):
        if lims is not None:
            self.__ylims = lims
            return self
        else:
            return self.__ylims

    def xlims(self, lims = None):
        if lims is not None:
            self.__xlims = lims
            return self
        else:
            return self.__xlims


    # Processors and Pre-Processors

    def setup_xy_base(self, xllim = 0, xhlim = 1, yllim = 0, yhlim = 1):
        self.ylims((yllim, yhlim))
        self.xlims((xllim, xhlim))

        self.pars(0).set_xlim(xllim, xhlim)
        self.pars(0).set_ylim(yllim, yhlim)

        self.pars(0).set_xticks([])
        self.pars(0).set_yticks([])

        self.pars(0).tick_params(labelbottom = False, bottom = False, labelleft = False, left = False, labelright = False, right = False, labeltop = False, top = False, which = "both", axis = "both", reset = True)

        self.pars(0).get_xaxis().set_visible(False)
        self.pars(0).get_yaxis().set_visible(False)

    def setup_td_xb1_yl1(self, xlabel, ylabel, xllim, xhlim, yllim, yhlim, xnbins = 10, ynbins = 20, minorticks = True, grid = True):
        self.host().autoscale(False)

        self.host().set_xscale("linear")
        self.host().set_xlim(xllim, xhlim)
        self.host().set_ylim(yllim, yhlim)

        self.host().set_xlabel(xlabel)
        self.host().set_ylabel(ylabel)

        self.host().locator_params(axis = 'x', nbins = xnbins)
        self.host().locator_params(axis = 'y', nbins = ynbins)

        self.host().tick_params(labelbottom = True, bottom = True, labelleft = True, left = True, labelright = False, right = False, labeltop = False, top = False, which = "both", axis = "both")

        self.host().get_xaxis().set_ticks_position("bottom")
        self.host().get_yaxis().set_ticks_position("left")

        self.host().get_xaxis().set_label_position("bottom")
        self.host().get_yaxis().set_label_position("left")

        self.host().get_xaxis().set_visible(True)
        self.host().get_yaxis().set_visible(True)

        if minorticks is True:
            self.host().minorticks_on()

        if grid is True:
            self.host().grid(color = "white", linestyle = "--", linewidth = 0.3, which = "major", axis = "both")

    def setup_fd_xy(self, layer, xlabel, ylabel, xllim, xhlim, yllim, yhlim, xnbins = 20, ynbins = 20, minorticks = True, grid = True, xlog = False, label_bl = True):
        layer.autoscale(False)

        if xlog is True:
            layer.set_xscale("log", nonpositive = "clip", base = 10)
            fmt = ScalarFormatter()
            fmt.set_scientific(False)
            layer.get_xaxis().set_major_formatter(fmt)
            layer.set_xticks([ j * 10**i for i in range(int(np.log10(xllim)), int(np.log10(xhlim)) + 1) for j in [ 1, 2, 5 ] ])

        layer.set_xlim(xllim, xhlim)
        layer.set_ylim(yllim, yhlim)

        layer.set_xlabel(xlabel)
        layer.set_ylabel(ylabel)

        if xlog is False:
            layer.locator_params(axis = 'x', nbins = xnbins)

        layer.locator_params(axis = 'y', nbins = ynbins)

        if label_bl is True:
            layer.tick_params(labelbottom = True, bottom = True, labelleft = True, left = True, labelright = False, right = False, labeltop = False, top = False, which = "both", axis = "both")

            layer.get_xaxis().set_ticks_position("bottom")
            layer.get_yaxis().set_ticks_position("left")

            layer.get_xaxis().set_label_position("bottom")
            layer.get_yaxis().set_label_position("left")
        else:
            layer.tick_params(labelbottom = False, bottom = False, labelleft = False, left = False, labelright = True, right = True, labeltop = True, top = True, which = "both", axis = "both")

            layer.get_xaxis().set_ticks_position("top")
            layer.get_yaxis().set_ticks_position("right")

            layer.get_xaxis().set_label_position("top")
            layer.get_yaxis().set_label_position("right")

        layer.get_xaxis().set_visible(True)
        layer.get_yaxis().set_visible(True)

        if minorticks is True:
            layer.minorticks_on()

        if grid is True:
            layer.grid(visible = True, color = "white", linestyle = ':', linewidth = 0.1, which = "both", axis = "both")

    def setup_fd_xb1_yl1(self, xlabel, ylabel, xllim, xhlim, yllim, yhlim, xnbins = 20, ynbins = 20, minorticks = True, grid = True, xlog = False):
        self.setup_fd_xy(self.host(), xlabel, ylabel, xllim, xhlim, yllim, yhlim, xnbins, ynbins, minorticks, grid, xlog, label_bl = True)

    def setup_fd_xt1_yr1(self, xlabel, ylabel, xllim, xhlim, yllim, yhlim, xnbins = 20, ynbins = 20, minorticks = True, grid = True, xlog = False):
        self.setup_fd_xy(self.pars(1), xlabel, ylabel, xllim, xhlim, yllim, yhlim, xnbins, ynbins, minorticks, grid, xlog, label_bl = False)

    def setup_sub_fdp(self, xllim, xhlim, yllim = -1, yhlim = 1, edgecolor = "gray"):
        self.subs(0).autoscale(False)

        self.subs(0).set_xlim(xllim, xhlim)
        self.subs(0).set_ylim(yllim, yhlim)

        self.subs(0).tick_params(direction = "in", axis = "both", labelleft = False, labelbottom = False, top = False, bottom = False)

        for sp in self.subs(0).spines.values():
            sp.set_edgecolor(edgecolor)

        self.subs(0).get_xaxis().set_visible(True)
        self.subs(0).get_yaxis().set_visible(True)


    # Event handlers

    def event_button_press(self, e):
        if e.dblclick and e.button == 1:
            # Double-click from Left button
            self.eqi().events([ "event_freq_base", e.xdata ])

    def event_key_press(self, e):
        try:
            n = int(e.key)
        except ValueError:
            return

        if n in range(0, 9):
            self.eqi().events([ "event_view_mode", n ])

    def event_close(self, e):
        self.eqi().events([ "event_close", True ])


    # Plotters

    def norm2abs_coord_conv(self, xn, yn):
        # Convert normalized coordiantes (0:1) to real (absolute) plot coordinates of the host
        ydim = abs(self.ylims()[0] - self.ylims()[1])
        xdim = abs(self.xlims()[0] - self.xlims()[1])

        return (((xn * xdim) + self.xlims()[0]), ((yn * ydim) + self.ylims()[0]))

    def plot_signal(self, x, y, linewidth = 0.3, label = "Time", color = "yellow", zorder = 10, antialiased = True, plot_id = None):
        if plot_id is None:
            plot_id = len(self.plots())

        return self.plots(plot_id, self.host().plot(x, y, linewidth = linewidth, label = label, color = color, zorder = zorder, antialiased = antialiased)[0])

    def plot_spectrum_magn(self, x, y, linewidth = 0.3, label = "Frequency", color = "red", zorder = 9, antialiased = True, plot_id = None):
        if plot_id is None:
            plot_id = len(self.plots())

        return self.plots(plot_id, self.pars(1).plot(x, y, linewidth = linewidth, label = label, color = color, zorder = zorder, antialiased = antialiased)[0])

    def plot_spectrum_phase(self, x, y, linewidth = 0.1, label = "Phase", color = "green", zorder = 9, antialiased = True, plot_id = None):
        if plot_id is None:
            plot_id = len(self.plots())

        return self.plots(plot_id, self.subs(0).plot(x, y, linewidth = linewidth, label = label, color = color, zorder = zorder, antialiased = antialiased)[0])

    def plot_text(self, text, xo, yo, color = "white", weight = "normal", host = True, par = None, normalized_xy = True):
        x, y = self.norm2abs_coord_conv(xo, yo) if normalized_xy is True else (xo, yo)

        if host is True:
            self.host().text(x, y, text, color = color, weight = weight)
        elif par is not None:
            self.pars(par).text(x, y, text, color = color, weight = weight)

    def plot_hline(self, y, color = 'green', linestyle = "--", linewidth = 0.5, legend = None, legend_xo = None, legend_yo = None, on_host = False, par = None, zorder = 20):
        if on_host is True:
            self.host().axhline(y, color = color, linestyle = linestyle, linewidth = linewidth, zorder = zorder)
        else:
            self.pars(par).axhline(y, color = color, linestyle = linestyle, linewidth = linewidth, zorder = zorder)

        if legend is not None and legend_xo is not None and legend_yo is not None:
            self.plot_text(legend, legend_xo, legend_yo, color = color, weight = "bold")

    def plot_measurements(self, mdict, xo, yo, xspacing = 0.2, yspacing = 0.1, kvspacing = 0.075, varsperline = 4, color = "white"):
        offset_x = 0
        offset_y = 0
        count = 0

        for k in mdict:
            self.plot_text(k, xo + offset_x, yo + offset_y, color = color, weight = "bold", host = False, par = 0)
            self.plot_text(": %s %s" % (mdict[k][0], mdict[k][1]), xo + offset_x + kvspacing, yo + offset_y, color = color, host = False, par = 0)

            count += 1
            offset_x += xspacing

            if not (count % varsperline):
                # New line
                offset_y += yspacing
                offset_x = 0

    def plot_peaks(self, peaks, xo, yo, xspacing = 0.2, yspacing = 0.1, kvspacing = 0.075, varsperline = 5, color = "white", chart_peaks_count = 6):
        offset_x = 0
        offset_y = 0
        count = 0

        for count,p in enumerate(peaks):
            if count < chart_peaks_count:
                self.plot_text("%d" % (count + 1), p[0], p[1], color = "white", host = False, par = 1, normalized_xy = False)

            # Plot even harmonics in green, odd harmonics in red
            self.plot_text("%d" % (count + 1), xo + offset_x, yo + offset_y, color = color if not p[3] else "green" if p[4] else "red", weight = "bold", host = False, par = 0)
            self.plot_text(": %.3f Hz, %.2f %s" % (p[0], p[1], self.dci().log_unit()), xo + offset_x + kvspacing, yo + offset_y, color = color, host = False, par = 0)

            count += 1
            offset_x += xspacing

            if not (count % varsperline):
                # New line
                offset_y += yspacing
                offset_x = 0

    def plot_peaks_idx(self, tfreqs):
        for count,f in enumerate(tfreqs):
            self.plot_text("%d" % (count + 1), f[0], f[1], color = "white", host = False, par = 1, normalized_xy = False)

    def plot_test_metric(self, x, y, color = None, linestyle = None, linewidth = None, label = None, plot_id = None, on_host = False, par = 1, zorder = 20, delta = True):
        if plot_id is None:
            plot_id = len(self.plots())

        if on_host is True:
            self.plots(plot_id, self.host().plot(x, y, color = color, linestyle = linestyle, linewidth = linewidth, label = label + ((" [\u0394: %.3f]" % np.array(y).ptp()) if delta is True else ""), zorder = zorder)[0])
        else:
            self.plots(plot_id, self.pars(par).plot(x, y, color = color, linestyle = linestyle, linewidth = linewidth, label = label + ((" [\u0394: %.3f]" % np.array(y).ptp()) if delta is True else ""), zorder = zorder)[0])

    def plot_hlines(self, hlines):
        for count,hl in enumerate(hlines):
            self.plot_hline(hlines[hl][0], color = hlines[hl][1], linestyle = hlines[hl][2], linewidth = hlines[hl][3], legend = hl, legend_xo = 0.1125 + (0.15 * count), legend_yo = 0.06, on_host = hlines[hl][4])


    # Render

    def pause(self, nsec = 0.001):
        plt.pause(nsec)

    def draw(self, pause = 0.001):
        plt.draw()
        plt.pause(pause)

    def show(self):
        plt.show()

    def render(self, legend_loc = "upper left", tight = True, pause = 0.001, single = False):
        self.host().legend(handles = self.plots(), loc = legend_loc, fontsize = "small")

        if tight is True:
            self.fig().tight_layout()

        if single is True:
            self.show()
        else:
            self.draw(pause)


