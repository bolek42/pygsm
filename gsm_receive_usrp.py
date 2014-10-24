#!/usr/bin/env python
#this file isn't ready to use now - gsm-receiver lacks realtime processing capability
#there are many underruns of buffer for samples from usrp's, many blocks of samples get lost and
#receiver isn't prepared for this situation too well

from gnuradio import gr, gru, blks2, eng_notation
#, gsm
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from optparse import OptionParser
from os import sys

#import gsm from airprobe
airporbepath = "/home/hammel/Build/gsm/airprobe/gsm-receiver"
for extdir in [airporbepath + '/debug/src/lib',
               airporbepath + '/debug/src/lib/.libs',
               airporbepath + '/src/lib',
               airporbepath + '/src/lib/.libs']:
    if extdir not in sys.path:
        sys.path.append(extdir)
import gsm

#gsm recv_callback
class tuner(gr.feval_dd):
    def __init__(self, target):
        gr.feval_dd.__init__(self)
        self.target = target

    def eval(self, freq_offet):
        self.target.set_center_freq(freq_offet)
        return freq_offet

#actual top_block
class synchronizer(gr.feval_dd):
    def __init__(self, top_block):
        gr.feval_dd.__init__(self)
        self.top_block = top_block

    def eval(self, timing_offset):
        pass
        return freq_offet

class top_block(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)
        (options, args) = self._process_options()
        self.options    = options
        self.args       = args
        self.source = self._set_source()

        self.recv_blck, self.recv = self.gsm_receiver()

        self.connect(self.source, self.recv)


    def _set_source(self, usrp=True):
        options = self.options
        if usrp:
            self.usrp = uhd.usrp_source("master_clock_rate=52e6", uhd.io_type_t.COMPLEX_FLOAT32, 1)
            self.usrp.set_center_freq(self.options.freq)
            #self.usrp.set_gain(self.options.gain)
            self.usrp.set_samp_rate(400e3)
            return self.usrp
        else:
            self.blocks_file_source = blocks.file_source(gr.sizeof_gr_complex*1, "gsm.cfile", False)
            return self.blocks_file_source



    def gsm_receiver( self, input_rate = 400e3):
        filter_cutoff   = 145e3
        filter_t_width  = 10e3
        offset = 0

        #rates
        gsm_symb_rate = 1625000.0 / 6.0
        sps = input_rate / gsm_symb_rate / self.options.osr

        filter_taps    = gr.firdes.low_pass(1.0, input_rate, filter_cutoff, filter_t_width, gr.firdes.WIN_HAMMING)
        filtr          = gr.freq_xlating_fir_filter_ccf(1, filter_taps, offset, input_rate)
        interpolator   = gr.fractional_interpolator_cc(0, sps)

        tuner_callback = tuner(filtr)
        synchronizer_callback  = synchronizer(self)
        receiver       = gsm.receiver_cf( tuner_callback, synchronizer_callback, self.options.osr, self.options.key.replace(' ', '').lower(), self.options.configuration.upper())

        blocks = {}
        blocks[ "synchronizer_callback"]  = synchronizer_callback
        blocks[ "tuner_callback"]         = tuner_callback
        blocks[ "filter_taps"]            = filter_taps
        blocks[ "filtr"]                  = filtr
        blocks[ "interpolator"]           = interpolator
        blocks[ "receiver"]               = receiver
        self.connect( filtr,  interpolator, receiver)

        return blocks, filtr


    def _process_options(self):
        parser = OptionParser(option_class=eng_option)
        parser.add_option("-d", "--decim", type="int", default=9999,
                                    help="Set USRP decimation rate to DECIM [default=%default]")
        parser.add_option("-r", "--osr", type="int", default=4,
                          help="Oversampling ratio [default=%default]")
        parser.add_option("-I", "--inputfile", type="string", default="cfile",
                                    help="Input filename")
        parser.add_option("-O", "--outputfile", type="string", default="cfile2.out",
                                    help="Output filename")
        parser.add_option("-R", "--rx-subdev-spec", type="subdev", default=None,
                                    help="Select USRP Rx side A or B (default=first one with a daughterboard)")
        parser.add_option("-f", "--freq", type="eng_float", default="950.4M",
                                    help="set frequency to FREQ", metavar="FREQ")
        parser.add_option("-g", "--gain", type="eng_float", default=None,
                                    help="Set gain in dB (default is midpoint)")
        parser.add_option("-k", "--key", type="string", default="AD 6A 3E C2 B4 42 E4 00",
                          help="KC session key")
        parser.add_option("-c", "--configuration", type="string", default="",
                          help="Decoder configuration")

        (options, args) = parser.parse_args ()
        return (options, args)


if __name__ == '__main__':
    try:
        top_block().run()
    except KeyboardInterrupt:
        pass
