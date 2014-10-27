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

import taps #fft channelizer taps

class top_block(grc_wxgui.top_block_gui):
    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Top Block")

        #configure channelizer
        self.process_options()
        self.gsm_channelizer_config()

        #setting source
        self.src = self.source()
        self.channelizer_in, self.channelizer_out = self.fft_channelizer( self.fft_len, self.channel_bins)
        self.connect((self.src, 0), (self.channelizer_in, 0))
        self.sinks( self.channelizer_out, self.options.arfcns)

    ############################################
    #       Source                             #
    ############################################
    def source( self):
        cfile = self.options.inputfile
        if cfile != "":
            self.file_source = blocks.file_source(gr.sizeof_gr_complex*1, cfile, True)
            self.throttle = blocks.throttle(gr.sizeof_gr_complex*1, self.samp_rate)
            self.connect((self.file_source, 0), (self.throttle, 0))
            src = self.throttle
        else:
            self.usrp = uhd.usrp_source( "", uhd.io_type_t.COMPLEX_FLOAT32, 1)
            self.usrp.set_samp_rate( self.samp_rate)
            self.usrp.set_center_freq( self.f_center)
            src = self.usrp

        self.waterfallsink = waterfallsink2.waterfall_sink_c(
            self.GetWin(),
            baseband_freq=self.f_center,
            dynamic_range=100,
            ref_level=0,
            ref_scale=2.0,
            sample_rate=self.samp_rate,
            fft_size=512,
            fft_rate=15,
            average=False,
            avg_alpha=None,
            title="Waterfall Plot",
        )
        self.Add(self.waterfallsink.win)
        self.connect((src, 0), (self.waterfallsink, 0))

        return src

    ############################################
    #       Channelizer                        #
    ############################################
    def fft_channelizer( self, fft_len, channel_bins):
        #do a fwd fft
        self.fft_channelizer_s2v = blocks.stream_to_vector( gr.sizeof_gr_complex*1, fft_len)
        self.fft_channelizer_fft_fwd = fft.fft_vcc( fft_len, True, (window.blackmanharris(1024)), True, 1)
        self.fft_channelizer_v2s = blocks.vector_to_stream( gr.sizeof_gr_complex*1, fft_len)
        self.connect(   self.fft_channelizer_s2v,
                        self.fft_channelizer_fft_fwd,
                        self.fft_channelizer_v2s)

        #per channel
        self.fft_channelizer_skiphead = []
        self.fft_channelizer_keep_m_in_n = []
        self.fft_channelizer_stream2vector = []
        self.fft_channelizer_multiply_const = []
        self.fft_channelizer_fft_rev = []
        self.fft_channelizer_vector2stream = []
        for from_bin, to_bin in channel_bins:
            #output samp rate: samp_rate / (fft_len/keep)
            keep = to_bin - from_bin
            fft_channelizer_taps = taps.taps(keep)

            self.fft_channelizer_skiphead.append( blocks.skiphead(gr.sizeof_gr_complex*1, from_bin))
            self.fft_channelizer_keep_m_in_n.append( blocks.keep_m_in_n(gr.sizeof_gr_complex, keep, fft_len, 0))
            self.fft_channelizer_stream2vector.append( blocks.stream_to_vector(gr.sizeof_gr_complex*1, keep))
            self.fft_channelizer_multiply_const.append( blocks.multiply_const_vcc(fft_channelizer_taps))
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

    ############################################
    #       Sinks                              #
    ############################################
    def sinks( self, src, arfcns):
        nullsink = True
        #udp sinks
        port = self.options.port
        if port != 0:
            nullsink = False
            self.udp_sink = []
            for s,arfcn in zip(src, arfcns):
                self.udp_sink.append( blocks.udp_sink( gr.sizeof_gr_complex*1, "127.0.0.1", port, 1472, True) )
                self.connect( s, self.udp_sink[-1] )
                print "Arfcn %d @ UDP %d" % (arfcn, port)
                port += 1

        #file sink
        outdir = self.options.outputdir
        if outdir != "":
            nullsink = False
            self.file_sink = []
            for s,arfcn in zip(src, arfcns):
                self.file_sink.append( blocks.file_sink(gr.sizeof_gr_complex*1, "%s/arfcn_%d.cfile" % (outdir, arfcn)))
                self.connect( s, self.file_sink[-1] )

        if nullsink:
            self.null_sink = []
            for s,arfcn in zip(src, arfcns):
                self.null_sink.append( blocks.null_sink(gr.sizeof_gr_complex*1))
                self.connect( s, self.null_sink[-1] )



    ############################################
    #       Options and Config                 #
    ############################################
    def process_options(self):
        parser = OptionParser(option_class=eng_option)
        parser.add_option( "-a", "--arfcns", type="str", default="",
                          help="List of arfcns to channelize e.g. 12,45,32,22")
        parser.add_option( "-f", "--freq", type="eng_float", default="0",
                          help="Center freq [default=%fefault]", metavar="FREQ")
        parser.add_option( "-s", "--samp-rate", type="eng_float", default="0",
                          help="Center freq [default=%fefault]", metavar="FREQ")
        parser.add_option( "-I", "--inputfile", type="string", default="",
                          help="Input filename")
        parser.add_option( "-O", "--outputdir", type="string", default="",
                          help="Output filename")
        parser.add_option( "-p", "--port", type="int", default="0",
                          help="UDP Port for first channel")
        (options, args) = parser.parse_args ()

        #parsing arfcn list
        arfcns = []
        for arfcn in  options.arfcns.split(","):
            arfcns.append( int( arfcn ))

        options.arfcns = arfcns

        self.options = options


    def gsm_arfcn2f( self, arfcn):
        if arfcn < 125:
            return 935e6 + 200e3 * arfcn
        if arfcn > 125:
            return 1805.2e6 + 200e3 * (arfcn-512)
        else:
            print "invalid arfcn %d" % arfcn
            return 0

    def gsm_channelizer_config( self):
        #reading options
        arfcns = self.options.arfcns
        f_center = self.options.freq
        samp_rate = self.options.samp_rate

        #center frequency
        f_min = self.gsm_arfcn2f( min( arfcns))
        f_max = self.gsm_arfcn2f( max( arfcns))
        if f_center == 0:
            f_center = (f_max + f_min) / 2.0
        print "center frequency %.2fMHz" % (f_center / 1e6)
        self.f_center = f_center

        #sample rate
        bandwidth = f_max - f_min
        print "needed bandwidth %.2fM" % (bandwidth / 1e6)
        if samp_rate == 0:
            if bandwidth <= 1e6:
                samp_rate = 1e6
            elif bandwidth <= 2e6:
                samp_rate = 2e6
            elif bandwidth <= 4e6:
                samp_rate = 4e6
            elif bandwidth <= 8e6:
                samp_rate = 8e6
            elif bandwidth <= 16e6:
                samp_rate = 16e6
            elif bandwidth <= 32e6:
                samp_rate = 32e6
            else:
                print "too much bandwidth"
        print "sample rate %.2fM" % (samp_rate / 1e6)
        self.samp_rate = samp_rate

        #fft len
        #one bin is 2kHz
        f_bin = 2e3 #freq. per bin
        fft_len = int( samp_rate / f_bin)
        print "fft len %d" % (fft_len)
        self.fft_len = fft_len

        #compute channel_bins
        channel_bins = []
        for arfcn in arfcns:
            f = self.gsm_arfcn2f( arfcn)
            f_offset = f - f_center
            from_bin = int((f_offset - 200e3) / f_bin) + (fft_len / 2)
            to_bin = int((f_offset + 200e3) / f_bin) + (fft_len / 2)
            channel_bins.append((from_bin, to_bin))
            print "Arfcn %d @ %.2fMHz: %d %d" % (arfcn, f/1e6, from_bin, to_bin)
        self.channel_bins = channel_bins

if __name__ == '__main__':
	tb = top_block()
	tb.Run(True)

