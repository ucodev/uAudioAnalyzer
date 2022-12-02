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

import sys
import traceback

#
# import core interfaces
#
#  - Event Queue Interface (EQI)
#
from uaa_core import EQI

#
# import configuration interfaces:
#
#  - Common Configuration Interface (CCI)
#  - Device Calibration Interface (DCI)
#
from uaa_config import CCI, DCI

#
# import user interfaces
#
#  - Command Line Interface (CLI)
#
from uaa_ui import CLI

#
# import application interfaces:
#
#  - Application: Audio Ananalyzer (AAA)
#  - Application: Audio Meter (AAM)
#  - Application: Audio Test (AAT)
#  - Application: Interface Calibration (AIC)
#
from uaa_app import AAA, AAM, AAT, AIC

#
# Defaults
#
DEFAULT_DIR_TMP = "./tmp"
DEFAULT_DIR_SNAPSHOTS = "./snapshots"
DEFAULT_FILE_CAL = "./config/cal.json"
DEFAULT_FILE_CONFIG = "./config/config.json"

#
# Process exit status
#
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

#
# Debug status
#
DEBUG_ENABLE = True

#
# Abort handler
#
def aa_abort(e):
    print("Failed: %s" % e)
    sys.exit(EXIT_FAILURE)


### MAIN ###

if __name__ == '__main__':
    ## Process command line ##

    if DEBUG_ENABLE: print("Processing Command Line Interface...")

    try:
        cli = CLI(sys.argv)
    except Exception as e:
        CLI().usage(sys.argv)
        print("\nReason: %s\n" % e)
        sys.exit(EXIT_FAILURE)


    ## Process operation ##

    if cli.operation() == "meter":
        if DEBUG_ENABLE: print("Processing Device Calibration Interface...")
        try:
            dci = DCI(cal_file = DEFAULT_FILE_CAL)
        except Exception as e:
            aa_abort(e)

        # Application: Audio Meter
        if DEBUG_ENABLE: print("Loading Application: Audio Meter...")

        try:
            aam = AAM(cli, dci, tmp_dir = DEFAULT_DIR_TMP)
        except AssertionError as e:
            traceback.print_tb(sys.exc_info()[2])
            sys.exit(EXIT_FAILURE)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            aa_abort(e)
        else:
            while True:
                try:
                    aam.refresh()
                except StopIteration:
                    break
    elif cli.operation() == "test":
        try:
            cci = CCI(filename = DEFAULT_FILE_CONFIG)
        except Exception as e:
            aa_abort(e)

        # Application: Audio Test
        if DEBUG_ENABLE: print("Loading Application: Audio Test...")

        try:
            aat = AAT(cli, cci)
        except AssertionError as e:
            traceback.print_tb(sys.exc_info()[2])
            sys.exit(EXIT_FAILURE)
        except Exception as e:
            aa_abort(e)
    elif cli.operation() == "calibrate":
        # Application: Interface Calibration
        if DEBUG_ENABLE: print("Loading Application: Interface Calibration...")

        try:
            aic = AIC(cli, tmp_dir = DEFAULT_DIR_TMP)
        except AssertionError as e:
            traceback.print_tb(sys.exc_info()[2])
            sys.exit(EXIT_FAILURE)
        except Exception as e:
            aa_abort(e)
    elif cli.operation() == "analyze":
        try:
            cci = CCI(filename = DEFAULT_FILE_CONFIG)
        except Exception as e:
            aa_abort(e)

        if DEBUG_ENABLE: print("Processing Device Calibration Interface...")

        try:
            dci = DCI(cal_file = DEFAULT_FILE_CAL)
        except Exception as e:
            aa_abort(e)

        if DEBUG_ENABLE: print("Processing Event Handler Interface...")

        try:
            eqi = EQI()
        except Exception as e:
            aa_abort(e)

        # Application: Audio Analyzer
        if DEBUG_ENABLE: print("Loading Application: Audio Analyzer...")

        try:
            aaa = AAA(cli, dci, eqi, cci, freq_start = 15)
        except AssertionError as e:
            traceback.print_tb(sys.exc_info()[2])
            sys.exit(EXIT_FAILURE)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            aa_abort(e)
        else:
            while True:
                try:
                    aaa.refresh()
                except StopIteration:
                    break
    elif cli.operation() == "run":
        # TODO
        raise Exception("Not implemented")
    else:
        print("Unrecognized operation: %s" % sys.argv[1])
        sys.exit(EXIT_FAILURE)

    if DEBUG_ENABLE: print("Done.")

    sys.exit(EXIT_SUCCESS)


