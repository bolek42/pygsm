#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Fri Oct 24 03:04:19 2014
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

class top_block(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="Top Block")

		##################################################
		# Variables
		##################################################
		self.skip = skip = 2500
		self.samp_rate = samp_rate = 16e6
		self.keep = keep = 200
		self.fft_len = fft_len = 8000

		##################################################
		# Blocks
		##################################################
		self.wxgui_waterfallsink2_1 = waterfallsink2.waterfall_sink_c(
			self.GetWin(),
			baseband_freq=0,
			dynamic_range=100,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=samp_rate / (fft_len/keep),
			fft_size=512,
			fft_rate=15,
			average=False,
			avg_alpha=None,
			title="Waterfall Plot",
		)
		self.Add(self.wxgui_waterfallsink2_1.win)
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
		self.fft_vxx_1 = fft.fft_vcc(keep, False, (window.blackmanharris(1024)), True, 1)
		self.fft_vxx_0 = fft.fft_vcc(fft_len, True, (window.blackmanharris(1024)), True, 1)
		self.blocks_vector_to_stream_0_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, keep)
		self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, fft_len)
		self.blocks_udp_sink_0 = blocks.udp_sink(gr.sizeof_gr_complex*1, "127.0.0.1", 1337, 1472, True)
		self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate)
		self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, keep)
		self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_len)
		self.blocks_skiphead_0 = blocks.skiphead(gr.sizeof_gr_complex*1, skip)
		self.blocks_multiply_const_vxx_1 = blocks.multiply_const_vcc(([3.3027386574467086e-05, 7.530449030671414e-05, 0.00016530103281468393, 0.0003493911008977848, 0.000711233110397085, 0.0013946596828618902, 0.0026350235978981297, 0.004798194877209025, 0.00842327275699453, 0.014260794880177651, 0.02329364098706189, 0.03672455769782423, 0.055914415841515304, 0.08226092122025148, 0.1170192982944558, 0.16108302697492857, 0.2147600393405324, 0.2775920283882359, 0.3482658701540932, 0.4246533245032583, 0.5039894228038793, 0.5831675293759861, 0.659099532651724, 0.7290724636693747, 0.7910337917145012, 0.8437563875152905, 0.886864422805077, 0.920733628092362, 0.9463040008519988, 0.9648544454681403, 0.9777861783431654, 0.9864486969767231, 0.9920246178488873, 0.9954734645074557, 0.9975232854337563, 0.9986939772853741, 0.9993364486536307, 0.9996752532824711, 0.9998469370057872, 0.9999305344482086, 0.9999696492179403, 0.9999872354304371, 0.9999948332229748, 0.9999979873990753, 0.9999992456511154, 0.9999997279678726, 0.999999905623862, 0.9999999685034864, 0.9999999898891326, 0.9999999968781635, 0.9999999990729559, 0.9999999997352511, 0.9999999999272906, 0.9999999999807979, 0.9999999999951235, 0.9999999999988088, 0.9999999999997199, 0.9999999999999364, 0.9999999999999857, 0.9999999999999964, 0.9999999999999989, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999991, 0.9999999999999989, 0.9999999999999964, 0.9999999999999857, 0.9999999999999364, 0.9999999999997199, 0.9999999999988088, 0.9999999999951235, 0.9999999999807979, 0.9999999999272906, 0.9999999997352511, 0.9999999990729559, 0.9999999968781635, 0.9999999898891326, 0.9999999685034864, 0.999999905623862, 0.9999997279678726, 0.9999992456511154, 0.9999979873990753, 0.9999948332229748, 0.9999872354304371, 0.9999696492179403, 0.9999305344482086, 0.9998469370057872, 0.9996752532824711, 0.9993364486536307, 0.9986939772853741, 0.9975232854337563, 0.9954734645074557, 0.9920246178488873, 0.9864486969767231, 0.9777861783431654, 0.9648544454681403, 0.9463040008519988, 0.920733628092362, 0.886864422805077, 0.8437563875152905, 0.7910337917145012, 0.7290724636693747, 0.659099532651724, 0.5831675293759861, 0.5039894228038793, 0.4246533245032583, 0.3482658701540932, 0.2775920283882359, 0.2147600393405324, 0.16108302697492857, 0.1170192982944558, 0.08226092122025148, 0.055914415841515304, 0.03672455769782423, 0.02329364098706189, 0.014260794880177651, 0.00842327275699453, 0.004798194877209025, 0.0026350235978981297, 0.0013946596828618902, 0.000711233110397085, 0.0003493911008977848, 0.00016530103281468393, 7.530449030671414e-05]))
		self.blocks_keep_m_in_n_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, keep, fft_len, 0)
		self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, "/home/hammel/gsm/arfcn_85_sr_16M.cfile", True)

		##################################################
		# Connections
		##################################################
		self.connect((self.blocks_throttle_0, 0), (self.wxgui_waterfallsink2_0, 0))
		self.connect((self.blocks_file_source_0, 0), (self.blocks_throttle_0, 0))
		self.connect((self.blocks_throttle_0, 0), (self.blocks_stream_to_vector_0, 0))
		self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
		self.connect((self.fft_vxx_0, 0), (self.blocks_vector_to_stream_0, 0))
		self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_skiphead_0, 0))
		self.connect((self.blocks_skiphead_0, 0), (self.blocks_keep_m_in_n_0, 0))
		self.connect((self.blocks_keep_m_in_n_0, 0), (self.blocks_stream_to_vector_1, 0))
		self.connect((self.fft_vxx_1, 0), (self.blocks_vector_to_stream_0_0, 0))
		self.connect((self.blocks_vector_to_stream_0_0, 0), (self.wxgui_waterfallsink2_1, 0))
		self.connect((self.blocks_vector_to_stream_0_0, 0), (self.blocks_udp_sink_0, 0))
		self.connect((self.blocks_stream_to_vector_1, 0), (self.blocks_multiply_const_vxx_1, 0))
		self.connect((self.blocks_multiply_const_vxx_1, 0), (self.fft_vxx_1, 0))


	def get_skip(self):
		return self.skip

	def set_skip(self, skip):
		self.skip = skip

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.blocks_throttle_0.set_sample_rate(self.samp_rate)
		self.wxgui_waterfallsink2_0.set_sample_rate(self.samp_rate)
		self.wxgui_waterfallsink2_1.set_sample_rate(self.samp_rate / (self.fft_len/self.keep))

	def get_keep(self):
		return self.keep

	def set_keep(self, keep):
		self.keep = keep
		self.blocks_keep_m_in_n_0.set_m(self.keep)
		self.wxgui_waterfallsink2_1.set_sample_rate(self.samp_rate / (self.fft_len/self.keep))

	def get_fft_len(self):
		return self.fft_len

	def set_fft_len(self, fft_len):
		self.fft_len = fft_len
		self.blocks_keep_m_in_n_0.set_n(self.fft_len)
		self.wxgui_waterfallsink2_1.set_sample_rate(self.samp_rate / (self.fft_len/self.keep))

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = top_block()
	tb.Run(True)

