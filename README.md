## Summary

uCodev Audio Analyzer (uAudioAnalyzer) is a signal generator, time domain and frequency domain analyzer for audio frequency ranges.

It can be used with any sound card (or other specialized hardware) to acquire and generate signals.

Note that resulting accuracy is highly dependent on the quality of the hardware being used as an interface.

## Description

### Supported features

 * Time Domain and Frequency Domain graphical representations
 * THD, THD+N
 * SNR, SNRjitter
 * SFDR, ENOB
 * Phase Noise, Jitter
 * Frequency Response (FR) over supplied test ranges

## Examples

### All features ON

![All features ON](./examples/snapshots/uaa_gui_full.png?raw=true "All features on")

### Distortion, Noise, and Dynamic Range

![Distortion, Noise, and Dynamic Range](./examples/snapshots/uaa_gui_thdn_snr_sfdr.png?raw=true "Distortion, Noise, and Dynamic Range)

### Frequency Response

![Frequency Response](./examples/snapshots/uaa_gui_fr.png?raw=true "Frequency Response")

## License

uCodev Audio Analyzer is licensed under the [GNU Affero General Public License version 3](https://www.gnu.org/licenses/agpl-3.0.en.html)

## Dependencies

uAudioAnalyzer depends on the following Python3 packages:

* matplotlib
* numpy
* scipy
* soundfile

It will also depend on a few low-level libraries and command line tools being developed to remove its current dependencies from ALSA command-line tools (such as arecord and aplay) and make the meter, test and sweep interface faster, neater and better integrated. These libraries will be provided in a separate project (also open-source) when they are stable enough to be used by uAudioAnalyzer.

## Notes

* This project is an early stage of development, serving only as a PoC.

