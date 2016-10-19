#!/usr/bin/python2.7

from scapy.all import *
import socket
import SocketServer
from binascii import *


msgtype = {
    "NONE": 0,
    "FBSB_REQ": 1,
    "FBSB_CONF": 2,
    "DATA_IND": 3,
    "RACH_REQ": 4,
    "DM_EST_REQ": 5,
    "DATA_REQ": 6,
    "RESET_IND": 7,
    "PM_REQ": 8,
    "PM_CONF": 9,
    "ECHO_REQ": 10,
    "ECHO_CONF": 11,
    "RACH_CONF": 12,
    "RESET_REQ": 13,
    "RESET_CONF": 14,
    "DATA_CONF": 15,
    "CCCH_MODE_REQ": 16,
    "CCCH_MODE_CONF": 17,
    "DM_REL_REQ": 18,
    "PARAM_REQ": 19,
    "DM_FREQ_REQ": 20,
    "CRYPTO_REQ": 21,
    "SIM_REQ": 22,
    "SIM_CONF": 23,
    "TCH_MODE_REQ": 24,
    "TCH_MODE_CONF": 25,
    "NEIGH_PM_REQ": 26,
    "NEIGH_PM_IND": 27,
    "TRAFFIC_REQ": 28,
    "TRAFFIC_CONF": 29,
    "TRAFFIC_IND": 30 }

reset_type = {
    "RES_T_BOOT": 0,
    "RES_T_FULL": 1,
    "RES_T_SCHED": 2}

ccch_mode = {
    "NONE": 0,
    "NON_COMBINED": 1,
    "COMBINED": 2}

# chan_nr
RSL_CHAN_NR_MASK = 0xf8
RSL_CHAN_Bm_ACCHs = 0x08
RSL_CHAN_Lm_ACCH = 0x10
RSL_CHAN_SDCCH4_ACCH = 0x20
RSL_CHAN_SDCCH8_ACCH = 0x40
RSL_CHAN_BCCH = 0x80
RSL_CHAN_RACH = 0x88
RSL_CHAN_PCH_AGCH = 0x90

class osmol1(Packet):
    fields_desc=[   ByteEnumField("msgtype", None, msgtype),
                    ByteField("flags",0),
                    ShortField("padding",0)]



class osmol1_reset_req(Packet):
    name = "l1ctl_reset"
    fields_desc = [
        ByteEnumField("type",1,reset_type),
        ByteField("padding",0),
        ByteField("padding",0),
        ByteField("padding",0)
    ]

class osmol1_fbsb_req(Packet):
    fields_desc = [
        ShortField("band_arfcn",None),
        ShortField("timeout",100),
        ShortField("freq_err_thresh1",11000-1000),
        ShortField("freq_err_thresh2",1000-200),
        ByteField("num_freqerr_avg",3),
        ByteField("flags",7),
        ByteField("sync_info_idx",0),
        ByteEnumField("ccch_mode",1,ccch_mode),
        ByteField("rxlev_exp",0)
    ]

class osmol1_dm_est_req(Packet):
    fields_desc = [
        ByteField("tsc",None),

        #h0
        ByteField("hsn",None),
        ByteField("maio",None),
        ByteField("n",None),
        ByteField("padding",None),
        #FieldListField("ma", None, ShortField("arfcn",0), count_from= lambda p: 64),

        ByteField("tch_mode",None),
        ByteField("audio_mode",None),
    ]
    

class osmol1_data(Packet):
    fields_desc = [
        ByteEnumField("chan_nr",8,{ 0xf8:"RSL_CHAN_NR_MASK",
                                    0x08:"RSL_CHAN_Bm_ACCHs",
                                    0x10:"RSL_CHAN_Lm_ACCHs",
                                    0x20:"RSL_CHAN_SDCCH4_ACCH",
                                    0x40:"RSL_CHAN_SDCCH8_ACCH",
                                    0x80:"RSL_CHAN_BCCH",
                                    0x88:"RSL_CHAN_RACH",
                                    0x90:"RSL_CHAN_PCH_AGCH"}),
        ByteField("link_id",0),
        ShortField("arfcn",0),
        IntField("frame_nr",0),
        ByteField("rx_level",0),
        ByteField("snr",0),
        ByteField("num_biterr",0),
        ByteField("fire_crc",0),
    ]

class osmol1_ccch_mode_req(Packet):
    fields_desc = [
        ByteEnumField("chan_mode",1,ccch_mode),
        ByteField("padding",0),
        ByteField("padding",0),
        ByteField("padding",0)
    ]

bind_layers(osmol1, osmol1_fbsb_req, msgtype=1)
bind_layers(osmol1, osmol1_data, msgtype=3)
bind_layers(osmol1, osmol1_dm_est_req, msgtype=5)
bind_layers(osmol1, osmol1_reset_req, msgtype=13)
bind_layers(osmol1, osmol1_ccch_mode_req, msgtype=16)

class l1ctl:
    def __init__(self, l1sock):
        #open socket
        self.sock = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.sock.connect(l1sock)

        #self.reset()

    def l1_send(self, pack):
        l = struct.pack("!H", len(pack))
        self.sock.send(l + str(pack))

    def l1_recv(self, raw=False):
        l = struct.unpack("!H", self.sock.recv(2))[0]
        buff = self.sock.recv(l)

        if raw:
            return buff
        return osmol1(buff)

    #preforms a full reset
    def reset(self):
        print "reset"
        pack = osmol1(msgtype=13) / osmol1_reset_req(type=1)
        self.l1_send(pack)

    def set_arfcn(self, arfcn):
        print "set arfcn %d" % arfcn
        pack = osmol1(msgtype=1) / osmol1_fbsb_req(band_arfcn=arfcn)
        self.l1_send(pack)

    #receive data
    def recv(self):
        while True:
            p = self.l1_recv()
            if p.msgtype == 3:
                return p

    def proxy(self, sockname):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            os.remove(sockname)
        except OSError:
            pass

        sock.bind(sockname)
        sock.listen(1)
        print "waiting for client"
        conn, addr = sock.accept()
        print "run"

        while 1:
            readable,_,_ = select.select([conn], [], [], 0)
            if readable:
                l = struct.unpack("!H", conn.recv(2))[0]
                buff = conn.recv(l)
                self.proxy_show_pack(buff)
                self.l1_send(buff)

            
            readable,_,_ = select.select([self.sock], [], [], 0)
            if readable:
                buff = self.l1_recv(raw=True)
                #self.proxy_show_pack(buff)
                l = struct.pack("!H", len(buff))
                conn.send(l + str(buff))

    def proxy_show_pack(self, pack):
        p = osmol1(pack)
        skip = [
            msgtype["RESET_REQ"],
            msgtype["DATA_IND"],
            msgtype["SIM_REQ"],
            msgtype["SIM_CONF"],
            msgtype["NEIGH_PM_REQ"],
            msgtype["NEIGH_PM_IND"],
            msgtype["RESET_REQ"],
            msgtype["FBSB_REQ"],
            msgtype["CCCH_MODE_REQ"],
        ]
        if p.msgtype in skip:
            return

        print repr(p)




l1 = l1ctl("/tmp/osmocom_l2")
l1.proxy("/tmp/osmocom_l2_proxy")

#l1.set_arfcn(22)
#
#sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#while True:
#    data = l1.recv()
#    print repr(data)
#
