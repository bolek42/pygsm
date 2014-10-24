#!/usr/bin/env python
#
# Copyright 2009 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

from gnuradio import gr, blks2, blocks
import os, time
from scipy import fftpack
from gnuradio.eng_option import eng_option
from optparse import OptionParser

class pfb_top_block(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)

        #parse the options
        parser = OptionParser(option_class=eng_option)
        parser.add_option("--inputfile", type="string", default="", help="set the input file")
        parser.add_option("--arfcn", type="int", default="0", help="set center ARFCN")
        parser.add_option("--srate", type="int", default="10000000", help="set sample frequency")
        parser.add_option("--outdir", type="string", default="out/", help="out directory")
        parser.add_option("--port", type="int", default="0", help="UDP port to listen for packets")
        (options, args) = parser.parse_args ()

        #self._output_rate = options.srate / options.decimation

        # Create a set of taps for the PFB channelizer
        self._taps = gr.firdes.low_pass_2(1, options.srate, 145e3, 10e3,
                                          attenuation_dB=100, window=gr.firdes.WIN_BLACKMAN_hARRIS)
        self._taps = [1]

        nchannels = int( options.srate / 200e3)
        print "Number of channels: ", nchannels

        self._o = 1#float (options.nchannels) / float (options.decimation);
        print "pfb oversampling: ", self._o

        # Construct the channelizer filter
        self.pfb = blks2.pfb_channelizer_ccf(nchannels, self._taps, self._o)

        # Construct a vector sink for the input signal to the channelizer
        self.input = gr.file_source(gr.sizeof_gr_complex, options.inputfile, False);
        # Connect the blocks
        self.connect(self.input, self.pfb)

        self.output_files = list();

        # Create a vector sink for each of nchannels output channels of the filter and connect it
        self.snks = list()
        for i in xrange(nchannels):
            arfcn = (options.arfcn/2) + i
            if arfcn in [74,75,76] or True:
                self.output_files.append(gr.file_sink(gr.sizeof_gr_complex, "./%s/arfcn_%d.cf" % (options.outdir, arfcn)))
            else:
                self.output_files.append(blocks.null_sink(gr.sizeof_gr_complex*1))

            self.connect((self.pfb, i), self.output_files[i])

def main():
    tstart = time.time()

    tb = pfb_top_block()
    tb.run()

    tend = time.time()
    print "Run time: %f" % (tend - tstart)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

