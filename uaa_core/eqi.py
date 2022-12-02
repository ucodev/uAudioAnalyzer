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



class EQI():
    ### (E)vent (Q)ueue (I)nterface ###

    # Properties

    __init_args = None  # Original __init__ arguments
    __refresh = None    # Refresh generator

    __enabled = None    # Set to True if events are enabled, otherwise False.
    __triggered = None  # Set to True if an event was triggered, otherwise False.
    __type = None       # Type of event
    __value = None      # The value of the event
    __events = []       # The queue of events

    __event_types = [ "event_close", "event_freq_base", "event_view_mode" ]


    # Initializers, Loaders and Reloaders

    def __init__(self, enabled = True, event_types = [ "event_close", "event_freq_base", "event_view_mode" ]):
        self.__init_args = [ enabled, event_types ]

        self.__refresh = self.load(*self.__init_args)

        try:
            self.refresh()
        except StopIteration:
            pass

    def load(self, enabled = True, event_types = [ "event_close", "event_freq_base", "event_view_mode" ]):
        self.enabled(enabled)
        self.event_types(event_types)
        self.triggered(False)

        while True:
            yield

            if not len(self.events()):
                self.triggered(False)
                continue

            e = self.events(pop = True)

            self.triggered(True)
            self.type(e[0])
            self.value(e[1])

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

    def enabled(self, status = None):
        if status is not None:
            self.__enabled = status
            return self
        else:
            return self.__enabled

    def event_types(self, types = None):
        if types is not None:
            self.__event_types = types
            return self
        else:
            return self.__event_types

    def triggered(self, status = None):
        if status is not None:
            self.__triggered = status
            return self
        else:
            return self.__triggered

    def type(self, key = None):
        if key is not None:
            self.__type = key
            return self
        else:
            return self.__type

    def value(self, val = None):
        if val is not None:
            self.__value = val
            return self
        else:
            return self.__value

    def events(self, event = None, reset = False, pop = False):
        if reset is True:
            self.__events = []
            return self

        if event is not None:
            if type(event) is not list or len(event) != 2:
                raise Exception("Invalid type for event. Must be a list of two elements.")

            if event[0] not in self.event_types():
                raise Exception("Invalid event type: %s" % event[0])

            self.__events.append(event)

            return self
        elif pop is True:
            return self.__events.pop(0)
        else:
            return self.__events


