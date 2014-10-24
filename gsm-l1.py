#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Wed Oct 15 10:18:17 2014
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import window
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.gr import firdes
from gnuradio.wxgui import forms
from gnuradio.wxgui import waterfallsink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx
import sys
from gnuradio import uhd

airporbepath = "/home/hammel/Build/gsm/airprobe/gsm-receiver"
for extdir in [airporbepath + '/debug/src/lib',
               airporbepath + '/debug/src/lib/.libs',
               airporbepath + '/src/lib',
               airporbepath + '/src/lib/.libs']:
    if extdir not in sys.path:
        sys.path.append(extdir)
import gsm

#airprobe callbacks
class tuner(gr.feval_dd):
    def __init__(self, target):
        gr.feval_dd.__init__(self)
        self.target = target

    def eval(self, freq_offet):
        self.target.set_center_freq(freq_offet)
        return freq_offet

class synchronizer(gr.feval_dd):
    def __init__(self, top_block):
        gr.feval_dd.__init__(self)
        self.top_block = top_block

    def eval(self, timing_offset):
        pass
        return freq_offet


#actual top block
class top_block(grc_wxgui.top_block_gui):
    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Top Block")

        #gsm_reciever callback & options & options
        self.tuner_callback = tuner(self)
        self.synchronizer_callback = synchronizer(self)

        (options, args) = self._process_options()
        self.options    = options
        self.args       = args

        ##################################################
        # Variables
        ##################################################
        self.samp_rate_gsm = samp_rate_gsm = 400e3
        self.samp_rate = samp_rate = 400e3
        self.lowpass = lowpass = samp_rate_gsm/2
        self.f_xlate_fine = f_xlate_fine = 0
        self.f_xlate = f_xlate = 0

        ##################################################
        # Blocks
        ##################################################
        #self.freq_text_box = forms.text_box(
        #    parent=self.GetWin(),
        #    value=self.f_xlate,
        #    callback=self.set_f_xlate,
        #    label='Frequency',
        #    converter=forms.float_converter(),
        #    proportion=0,
        #)
        self.wxgui_waterfallsink2_0 = waterfallsink2.waterfall_sink_c(
            self.GetWin(),
            baseband_freq=0,
            dynamic_range=100,
            ref_level=0,
            ref_scale=2.0,
            sample_rate=samp_rate,
            fft_size=512,
            fft_rate=15,
            average=False,
            avg_alpha=None,
            title="Waterfall Plot",
        )
        self.Add(self.wxgui_waterfallsink2_0.win)

        self.src = self.source()
        #self.src = self.source( "gsm.cfile")
        self.freq_xlating_fir = filter.freq_xlating_fir_filter_ccc(1, (1, ), f_xlate + f_xlate_fine, samp_rate)
        self.recv_blcks, self.recv = self.gsm_receiver( self.samp_rate_gsm)

        self.low_corase = gr.fir_filter_ccf(int(samp_rate/400e3), firdes.low_pass(1, samp_rate, 200e3, 100000, firdes.WIN_HAMMING, 6.76))

        ##################################################
        # Connections
        ##################################################
        #src
        self.connect((self.src, 0), (self.freq_xlating_fir, 0))

        #freq xlate
        self.connect((self.freq_xlating_fir, 0), (self.wxgui_waterfallsink2_0, 0))

        #filter and recv
        self.connect((self.freq_xlating_fir, 0), (self.low_corase, 0))
        self.connect((self.low_corase, 0), (self.recv, 0))

    def source( self):
        cfile = self.options.inputfile
        port = self.options.port
        if cfile != "":
            self.file_source = blocks.file_source(gr.sizeof_gr_complex*1, cfile, True)
            self.throttle = blocks.throttle(gr.sizeof_gr_complex*1, self.samp_rate)
            self.connect((self.file_source, 0), (self.throttle, 0))
            return self.throttle
        elif port != 0:
            print port
            self.udp_source = blocks.udp_source(gr.sizeof_gr_complex*1, "127.0.0.1", port, 1472, True)
            return self.udp_source
        else:
            self.usrp = uhd.usrp_source("", uhd.io_type_t.COMPLEX_FLOAT32, 1)
            self.usrp.set_samp_rate(self.samp_rate)
            self.usrp.set_center_freq(self.options.freq)
            print self.options.freq
            return self.usrp

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

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.wxgui_waterfallsink2_0.set_sample_rate(self.samp_rate)

    def get_f_xlate_fine(self):
        return self.f_xlate_fine

    def set_f_xlate_fine(self, f_xlate_fine):
        self.f_xlate_fine = f_xlate_fine
        self._f_xlate_fine_slider.set_value(self.f_xlate_fine)
        self._f_xlate_fine_text_box.set_value(self.f_xlate_fine)
        self.freq_xlating_fir.set_center_freq(self.f_xlate + self.f_xlate_fine)

    def get_f_xlate(self):
        return self.f_xlate

    def set_f_xlate(self, f_xlate):
        self.f_xlate = f_xlate
        self._f_xlate_slider.set_value(self.f_xlate)
        self._f_xlate_text_box.set_value(self.f_xlate)
        self.freq_xlating_fir.set_center_freq(self.f_xlate + self.f_xlate_fine)

    def _process_options(self):
        parser = OptionParser(option_class=eng_option)
        parser.add_option("-f", "--freq", type="eng_float", default="944.8M",
                          help="Center freq [default=%fefault]", metavar="FREQ")
        parser.add_option("-d", "--decim", type="int", default=128,
                          help="Set USRP decimation rate to DECIM [default=%default]")
        parser.add_option("-r", "--osr", type="int", default=4,
                          help="Oversampling ratio [default=%default]")
        parser.add_option("-I", "--inputfile", type="string", default="",
                          help="Input filename")
        parser.add_option("-O", "--outputfile", type="string", default="cfile2.out",
                          help="Output filename")
        parser.add_option("-k", "--key", type="string", default="AD 6A 3E C2 B4 42 E4 00",
                          help="KC session key")
        parser.add_option("-c", "--configuration", type="string", default="",
                          help="Decoder configuration")
        parser.add_option("--port", type="int", default="0",
                          help="UDP port to listen for packets")
        (options, args) = parser.parse_args ()
        return (options, args)

if __name__ == '__main__':
    tb = top_block()
    tb.Run(True)

