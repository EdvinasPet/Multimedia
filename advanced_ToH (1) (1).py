#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

''' Considering the threshold of human hearing. '''


import numpy as np
import math
import minimal
import logging

from basic_ToH import Threshold
from basic_ToH import Threshold__verbose

minimal.parser.add_argument('--divisions', type=int, default=1,
                            help='Number of divisions for each subband')

class AdvancedThreshold(Threshold):


    def compute_dwt(self, chunk, wavelet, levels):
        # Create a list to store the DWT coefficients of each sub-band
        dwt_coeffs = []
        # Iterate over the sub-bands of the data chunk
        for subband in chunk:
            # Compute the DWT of the sub-band using the specified wavelet and number of levels
            coeffs = pywt.wavedec(subband, wavelet, level=levels)
            # Append the DWT coefficients to the list
            dwt_coeffs.append(coeffs)
        return dwt_coeffs

    def analyze(self, chunk):
        chunk_DWT = super().analyze(chunk)  # run the DWT of the data chunk
        divisions = minimal.args.divisions  # read the number of divisions required by the 'divisions' argument
        chunk_DWT = self.divide_subbands(chunk_DWT, divisions)  # perform sub-band division
        # Compute the DWT for each sub-band
        dwt_coeffs = self.compute_dwt(chunk_DWT, 'db1', self.dwt_levels)
        # Quantize sub-bands as in the original class
        chunk_DWT[self.slices[0][0]] = (chunk_DWT[self.slices[0][0]] / self.quantization_steps[0]).astype(np.int32)
        for i in range(self.dwt_levels):
            chunk_DWT[self.slices[i+1]['d'][0]] = (chunk_DWT[self.slices[i+1]['d'][0]] / self.quantization_steps[i+1]).astype(np.int32)
        return chunk_DWT, dwt_coeffs  # return the quantized DWT and the DWT coefficients

    def synthesize(self, chunk_DWT, dwt_coeffs):
        divisions = minimal.args.divisions  # read the number of divisions required by the 'divisions' argument
        chunk_DWT = self.divide_subbands(chunk_DWT, divisions)  # perform sub-band division
        # Dequantitise sub-bands as in the original class
        chunk_DWT[self.slices[0][0]] = chunk_DWT[self.slices[0][0]] * self.quantization_steps[0]
        for i in range(self.dwt_levels):
            chunk_DWT[self.slices[i+1]['d'][0]] = chunk_DWT[self.slices[i+1]['d'][0]] * self.quantization_steps[i+1]
        # Synthesize each sub-band using the DWT coefficients
        synthesized_chunk = []
        for i, subband_coeffs in enumerate(dwt_coeffs)


  


class AdvancedThreshold__verbose(AdvancedThreshold, Threshold__verbose):
    pass


try:
    import argcomplete  # <tab> completion for argparse.
except ImportError:
    logging.warning("Unable to import argcomplete (optional)")

if __name__ == "__main__":
    minimal.parser.description = __doc__
    try:
        argcomplete.autocomplete(minimal.parser)
    except Exception:
        logging.warning("argcomplete not working :-/")
    minimal.args = minimal.parser.parse_known_args()[0]
    if minimal.args.show_stats or minimal.args.show_samples:
        intercom = AdvancedThreshold__verbose()
    else:
        intercom = AdvancedThreshold()
    try:
        intercom.run()
    except KeyboardInterrupt:
        minimal.parser.exit("\nSIGINT received")
    finally:
        intercom.print_final_averages()