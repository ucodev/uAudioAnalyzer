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


import json


class CCI():
    ### (C)ommon (C)onfiguration (I)nterface ###

    # Properties

    __init_args = None  # Original __init__ arguments
    __refresh = None    # Refresh generator

    __filename = None   # Configuration file name
    __config = None     # Configuration dict


    # Initializers, Loaders and Reloaders

    def __init__(self, filename = "config.json"):
        self.__init_args = [ filename ]

        self.__refresh = self.load(*self.__init_args)

        try:
            self.refresh()
        except StopIteration:
            pass

    def load(self, filename = "config.json"):
        a = self.filename(filename)

        while True:
            try:
                with open(self.filename(), "r") as f:
                    self.config(json.loads(f.read()))
            except Exception as e:
                raise Exception("Unable to load configuration file: %s" % filename)

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

    def filename(self, file = None):
        if file is not None:
            self.__filename = file
            return self
        else:
            return self.__filename

    def config(self, data = None):
        if data is not None:
            self.__config = data
            return self
        else:
            return self.__config


    # Helpers

    def freq_nearest(self, freq):
        return min(self.config()["common"]["test_freqs"], key = lambda f: abs(f - int(freq)))


