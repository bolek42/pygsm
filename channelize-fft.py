#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Sun Oct 26 13:38:23 2014
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import gr
from gnuradio import window
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from gnuradio.wxgui import waterfallsink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx
from gnuradio import uhd

class top_block(grc_wxgui.top_block_gui):
    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Top Block")

        ##################################################
        # Variables
        ##################################################
        (options, args) = self._process_options()
        self.options    = options
        self.args       = args

        self.samp_rate = samp_rate = self.options.samp_rate
        self.fft_len = fft_len = 8000

        #setting source
        self.src = self.source()
        self.waterfallsink = waterfallsink2.waterfall_sink_c(
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
        self.Add(self.waterfallsink.win)
        self.connect((self.src, 0), (self.waterfallsink, 0))

        #add channelizer
        channels = [(3900,4100),(4100,4300)]
        self.channelizer_in, self.channelizer_out = self.fft_channelizer( channels)
        self.connect((self.src, 0), (self.channelizer_in, 0))
        self.sinks( self.channelizer_out)


    def source( self):
        cfile = self.options.inputfile
        if cfile != "":
            self.file_source = blocks.file_source(gr.sizeof_gr_complex*1, cfile, True)
            self.throttle = blocks.throttle(gr.sizeof_gr_complex*1, self.samp_rate)
            self.connect((self.file_source, 0), (self.throttle, 0))
            return self.throttle
        else:
            self.usrp = uhd.usrp_source( "", uhd.io_type_t.COMPLEX_FLOAT32, 1)
            self.usrp.set_samp_rate(self.samp_rate)
            self.usrp.set_center_freq(self.options.freq)
            print self.options.freq
            return self.usrp

    def fft_channelizer( self, channels):
        fft_len = self.fft_len

        #do a fwd fft
        self.fft_channelizer_s2v = blocks.stream_to_vector( gr.sizeof_gr_complex*1, fft_len)
        self.fft_channelizer_fft_fwd = fft.fft_vcc( fft_len, True, (window.blackmanharris(1024)), True, 1)
        self.fft_channelizer_v2s = blocks.vector_to_stream( gr.sizeof_gr_complex*1, fft_len)
        self.connect(   self.fft_channelizer_s2v,
                        self.fft_channelizer_fft_fwd,
                        self.fft_channelizer_v2s)

        #copmpute!
        self.fft_channelizer_taps = [3.3027386574467086e-05, 7.530449030671414e-05, 0.00016530103281468393, 0.0003493911008977848, 0.000711233110397085, 0.0013946596828618902, 0.0026350235978981297, 0.004798194877209025, 0.00842327275699453, 0.014260794880177651, 0.02329364098706189, 0.03672455769782423, 0.055914415841515304, 0.08226092122025148, 0.1170192982944558, 0.16108302697492857, 0.2147600393405324, 0.2775920283882359, 0.3482658701540932, 0.4246533245032583, 0.5039894228038793, 0.5831675293759861, 0.659099532651724, 0.7290724636693747, 0.7910337917145012, 0.8437563875152905, 0.886864422805077, 0.920733628092362, 0.9463040008519988, 0.9648544454681403, 0.9777861783431654, 0.9864486969767231, 0.9920246178488873, 0.9954734645074557, 0.9975232854337563, 0.9986939772853741, 0.9993364486536307, 0.9996752532824711, 0.9998469370057872, 0.9999305344482086, 0.9999696492179403, 0.9999872354304371, 0.9999948332229748, 0.9999979873990753, 0.9999992456511154, 0.9999997279678726, 0.999999905623862, 0.9999999685034864, 0.9999999898891326, 0.9999999968781635, 0.9999999990729559, 0.9999999997352511, 0.9999999999272906, 0.9999999999807979, 0.9999999999951235, 0.9999999999988088, 0.9999999999997199, 0.9999999999999364, 0.9999999999999857, 0.9999999999999964, 0.9999999999999989, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999989, 0.9999999999999964, 0.9999999999999857, 0.9999999999999364, 0.9999999999997199, 0.9999999999988088, 0.9999999999951235, 0.9999999999807979, 0.9999999999272906, 0.9999999997352511, 0.9999999990729559, 0.9999999968781635, 0.9999999898891326, 0.9999999685034864, 0.999999905623862, 0.9999997279678726, 0.9999992456511154, 0.9999979873990753, 0.9999948332229748, 0.9999872354304371, 0.9999696492179403, 0.9999305344482086, 0.9998469370057872, 0.9996752532824711, 0.9993364486536307, 0.9986939772853741, 0.9975232854337563, 0.9954734645074557, 0.9920246178488873, 0.9864486969767231, 0.9777861783431654, 0.9648544454681403, 0.9463040008519988, 0.920733628092362, 0.886864422805077, 0.8437563875152905, 0.7910337917145012, 0.7290724636693747, 0.659099532651724, 0.5831675293759861, 0.5039894228038793, 0.4246533245032583, 0.3482658701540932, 0.2775920283882359, 0.2147600393405324, 0.16108302697492857, 0.1170192982944558, 0.08226092122025148, 0.055914415841515304, 0.03672455769782423, 0.02329364098706189, 0.014260794880177651, 0.00842327275699453, 0.004798194877209025, 0.0026350235978981297, 0.0013946596828618902, 0.000711233110397085, 0.0003493911008977848, 0.00016530103281468393, 7.530449030671414e-05]

        #per channel
        self.fft_channelizer_skiphead = []
        self.fft_channelizer_keep_m_in_n = []
        self.fft_channelizer_stream2vector = []
        self.fft_channelizer_multiply_const = []
        self.fft_channelizer_fft_rev = []
        self.fft_channelizer_vector2stream = []
        for from_bin, to_bin in channels:
            #output samp rate: samp_rate / (fft_len/keep)
            keep = to_bin - from_bin

            self.fft_channelizer_skiphead.append( blocks.skiphead(gr.sizeof_gr_complex*1, from_bin))
            self.fft_channelizer_keep_m_in_n.append( blocks.keep_m_in_n(gr.sizeof_gr_complex, keep, fft_len, 0))
            self.fft_channelizer_stream2vector.append( blocks.stream_to_vector(gr.sizeof_gr_complex*1, keep))
            self.fft_channelizer_multiply_const.append( blocks.multiply_const_vcc(self.fft_channelizer_taps))
            self.fft_channelizer_fft_rev.append( fft.fft_vcc( keep, False, (window.blackmanharris(1024)), True, 1))
            self.fft_channelizer_vector2stream.append( blocks.vector_to_stream( gr.sizeof_gr_complex*1, keep))

            self.connect(   self.fft_channelizer_v2s,
                            self.fft_channelizer_skiphead[-1],
                            self.fft_channelizer_keep_m_in_n[-1],
                            self.fft_channelizer_stream2vector[-1],
                            self.fft_channelizer_multiply_const[-1],
                            self.fft_channelizer_fft_rev[-1],
                            self.fft_channelizer_vector2stream[-1])


        return self.fft_channelizer_s2v, self.fft_channelizer_vector2stream

    def sinks( self, src):
        port = 1337
        if port != 0:
            #udp sinks
            self.udp_sink = []
            for s in src:
                self.udp_sink.append( blocks.udp_sink( gr.sizeof_gr_complex*1, "127.0.0.1", port, 1472, True) )
                self.connect( s, self.udp_sink[-1] )
                port += 1

    def _process_options(self):
        parser = OptionParser(option_class=eng_option)
        parser.add_option("-f", "--freq", type="eng_float", default="944.8M",
                          help="Center freq [default=%fefault]", metavar="FREQ")
        parser.add_option("-s", "--samp-rate", type="eng_float", default="16M",
                          help="Center freq [default=%fefault]", metavar="FREQ")
        parser.add_option("-I", "--inputfile", type="string", default="",
                          help="Input filename")
        parser.add_option("-O", "--outputfile", type="string", default="cfile2.out",
                          help="Output filename")
        parser.add_option("--port", type="int", default="0",
                          help="UDP port to listen for packets")
        (options, args) = parser.parse_args ()
        return (options, args)


if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = top_block()
	tb.Run(True)

