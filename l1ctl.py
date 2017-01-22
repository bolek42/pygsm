#!/usr/bin/python2.7

from scapy.all import *
import socket
import SocketServer
from binascii import *
import gsmtap

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
    "BOOT": 0,
    "FULL": 1,
    "SCHED": 2}

ccch_mode = {
    "NONE": 0,
    "NON_COMBINED": 1,
    "COMBINED": 2}

channel_type = {
    "Bm_ACCHs": 0b00001,
    "Lm_ACCHs#0": 0b00010,
    "Lm_ACCHs#1": 0b00011,
    "SDCCH4_ACCH#0": 0b00100,
    "SDCCH4_ACCH#1": 0b00101,
    "SDCCH4_ACCH#2": 0b00110,
    "SDCCH4_ACCH#3": 0b00111,
    "SDCCH8_ACCH#0": 0b01000,
    "SDCCH8_ACCH#1": 0b01001,
    "SDCCH8_ACCH#2": 0b01010,
    "SDCCH8_ACCH#3": 0b01011,
    "SDCCH8_ACCH#4": 0b01100,
    "SDCCH8_ACCH#5": 0b01101,
    "SDCCH8_ACCH#6": 0b01110,
    "SDCCH8_ACCH#7": 0b01111,
    "BCCH":0b10000,
    "RACH":0b10001,
    "PCH_AGCH":0b10010}

#GSM 08.58 9.3.1
#channeltype, subslot
def channel_type2gsmtap(channel_type):
    if channel_type == 0b00001:
        return gsmtap.channel_type["TCH_F"],0
    if ((channel_type ^ 0b00010) & 0b11110)  == 0:
        return gsmtap.channel_type["TCH_H"], channel_type & 0b00001
    if ((channel_type ^ 0b00100) & 0b11100)  == 0:
        return gsmtap.channel_type["SDCCH4"], channel_type & 0b00011
    if ((channel_type ^ 0b01000) & 0b11000)  == 0:
        return gsmtap.channel_type["SDCCH8"], channel_type & 0b00111
    if channel_type == 0b10000:
        return gsmtap.channel_type["BCCH"], 0
    if channel_type == 0b10001:
        return gsmtap.channel_type["RACH"], 0
    if channel_type == 0b10010:
        return gsmtap.channel_type["PCH"], 0
    return 0xff, 0xff


class osmol1(Packet):
    fields_desc=[   ByteEnumField("msgtype", None, msgtype),
                    ByteField("flags",0),
                    ShortField("",0)]


def osmol1_info_ul():
    return [
        BitEnumField("channel_type", 0x00, 5, channel_type),
        BitField("timeslot", 0x00, 3),
        ByteField("link_id",0),
        BitField("",0,16)]

def osmol1_info_dl():
    return [
        BitEnumField("channel_type", 0x00, 5, channel_type),
        BitField("timeslot", 0x00, 3),
        ByteField("link_id",0),
        ShortField("arfcn",0),
        IntField("frame_nr",0),
        ByteField("rx_level",0),
        ByteField("snr",0),
        ByteField("num_biterr",0),
        ByteField("fire_crc",0)]


class osmol1_reset(Packet):
    fields_desc = [
        ByteEnumField("type",1,reset_type),
        BitField("",0,24),
    ]

class osmol1_pm_req(Packet):
    fields_desc = [
        ByteField("type",1),
        BitField("",0,24),
        ShortField("arfcn_from",0),
        ShortField("arfcn_to",0)]

class osmol1_pm_conf(Packet):
    fields_desc = [
        ShortField("arfcn",0),
        ByteField("pm1",0),
        ByteField("pm2",0),]
bind_layers(osmol1_pm_conf, osmol1_pm_conf)

class osmol1_neigh_pm_req(Packet):
    fields_desc = [
        ByteField("n",0),
        ByteField("",0),
        FieldListField("band_arfcn", None, ShortField("arfcn",0), count_from= lambda p: 64),
        FieldListField("tn", None, ByteField("arfcn",0), count_from= lambda p: 64),
    ]

class osmol1_neigh_pm_ind(Packet):
    fields_desc = [
        ShortField("arfcn",0),
        ByteField("pm1",0),
        ByteField("pm2",0),
        ByteField("tn",0),
        ByteField("",0),
    ]
bind_layers(osmol1_neigh_pm_ind, osmol1_neigh_pm_ind)

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

class osmol1_fbsb_conf(Packet):
    fields_desc = osmol1_info_dl() + [
        ShortField("initial_freq_err",None),
        ByteField("result",None),
        ByteField("bsic",None)]

class osmol1_crypto_req(Packet):
    fields_desc = osmol1_info_ul() + [
        ByteField("algo",None),
        FieldListField("kc", None, XByteField("kc",0))]

class osmol1_dm_est_req(Packet):
    fields_desc = osmol1_info_ul() + [
        #dm_est_req
        ByteField("tsc",None),
        ByteField("h",None),

        #h0
        ByteField("hsn",None),
        ByteField("maio",None),
        ByteField("n",None),
        ByteField("",None),
        FieldListField("ma", None, ShortField("arfcn",0), count_from= lambda p: 64),

        #dm_est_req
        ByteField("tch_mode",None),
        ByteField("audio_mode",None),
    ]

class osmol1_par_req(Packet):
    fields_desc = osmol1_info_ul() + [
        ByteField("ta",None),
        ByteField("tx_power",None),
        ShortField("",24),
    ]

class osmol1_rach_req(Packet):
    fields_desc = osmol1_info_ul() + [
        ByteField("ra",None),
        ByteField("combined",None),
        ShortField("offset",0),
    ]
class osmol1_rach_conf(Packet):
    fields_desc = osmol1_info_dl()

class osmol1_data_ind(Packet):
    fields_desc = osmol1_info_dl()

class osmol1_data_conf(Packet):
    fields_desc = osmol1_info_dl()

class osmol1_data_req(Packet):
    fields_desc = osmol1_info_ul()

class osmol1_ccch_mode(Packet):
    fields_desc = [
        ByteEnumField("chan_mode",1,ccch_mode),
        BitField("",0,24),
    ]

bind_layers(osmol1, osmol1_fbsb_req, msgtype=msgtype["FBSB_REQ"])
bind_layers(osmol1, osmol1_fbsb_conf, msgtype=msgtype["FBSB_CONF"])
bind_layers(osmol1, osmol1_pm_req, msgtype=msgtype["PM_REQ"])
bind_layers(osmol1, osmol1_crypto_req, msgtype=msgtype["CRYPTO_REQ"])
bind_layers(osmol1, osmol1_pm_conf, msgtype=msgtype["PM_CONF"])
bind_layers(osmol1, osmol1_data_ind, msgtype=msgtype["DATA_IND"])
bind_layers(osmol1, osmol1_data_req, msgtype=msgtype["DATA_REQ"])
bind_layers(osmol1, osmol1_data_conf, msgtype=msgtype["DATA_CONF"])
bind_layers(osmol1, osmol1_rach_req, msgtype=msgtype["RACH_REQ"])
bind_layers(osmol1, osmol1_rach_conf, msgtype=msgtype["RACH_CONF"])
bind_layers(osmol1, osmol1_par_req, msgtype=msgtype["PARAM_REQ"])
bind_layers(osmol1, osmol1_dm_est_req, msgtype=msgtype["DM_EST_REQ"])
bind_layers(osmol1, osmol1_reset, msgtype=msgtype["RESET_REQ"])
bind_layers(osmol1, osmol1_reset, msgtype=msgtype["RESET_CONF"])
bind_layers(osmol1, osmol1_ccch_mode, msgtype=msgtype["CCCH_MODE_REQ"])
bind_layers(osmol1, osmol1_ccch_mode, msgtype=msgtype["CCCH_MODE_CONF"])
bind_layers(osmol1, osmol1_neigh_pm_req, msgtype=msgtype["NEIGH_PM_REQ"])
bind_layers(osmol1, osmol1_neigh_pm_ind, msgtype=msgtype["NEIGH_PM_IND"])


def bind_gsm(layer):
    bind_layers(layer, gsmtap.CCCH, channel_type=channel_type["RACH"])
    bind_layers(layer, gsmtap.CCCH, channel_type=channel_type["BCCH"])
    bind_layers(layer, gsmtap.CCCH, channel_type=channel_type["PCH_AGCH"])

    bind_layers(layer, gsmtap.LAPDM, channel_type=channel_type["SDCCH4_ACCH#0"])
    bind_layers(layer, gsmtap.LAPDM, channel_type=channel_type["SDCCH4_ACCH#1"])
    bind_layers(layer, gsmtap.LAPDM, channel_type=channel_type["SDCCH4_ACCH#2"])
    bind_layers(layer, gsmtap.LAPDM, channel_type=channel_type["SDCCH4_ACCH#3"])

    bind_layers(layer, gsmtap.LAPDM, channel_type=channel_type["SDCCH8_ACCH#0"])
    bind_layers(layer, gsmtap.LAPDM, channel_type=channel_type["SDCCH8_ACCH#1"])
    bind_layers(layer, gsmtap.LAPDM, channel_type=channel_type["SDCCH8_ACCH#2"])
    bind_layers(layer, gsmtap.LAPDM, channel_type=channel_type["SDCCH8_ACCH#3"])
    bind_layers(layer, gsmtap.LAPDM, channel_type=channel_type["SDCCH8_ACCH#4"])
    bind_layers(layer, gsmtap.LAPDM, channel_type=channel_type["SDCCH8_ACCH#5"])
    bind_layers(layer, gsmtap.LAPDM, channel_type=channel_type["SDCCH8_ACCH#6"])
    bind_layers(layer, gsmtap.LAPDM, channel_type=channel_type["SDCCH8_ACCH#7"])
    #"Bm_ACCHs"
    #"Lm_ACCHs#0"
    #"Lm_ACCHs#1"

bind_gsm(osmol1_data_ind)
bind_gsm(osmol1_data_req)
bind_gsm(osmol1_data_conf)


class l1ctl:
    def __init__(self, l1sock):
        #open socket
        self.sock = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.sock.connect(l1sock)
        self.reset()
        
        self.gsmtap_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    def l1_send(self, pack):
        l = struct.pack("!H", len(pack))
        self.sock.send(l + str(pack))

    def l1_recv(self, raw=False):
        l = struct.unpack("!H", self.sock.recv(2))[0]
        buff = self.sock.recv(l)

        if raw:
            return buff
        return osmol1(buff)

    def reset(self, t=1):
        pack = osmol1(msgtype=13) / osmol1_reset(type=t)
        self.l1_send(pack)

        while osmol1_reset not in self.l1_recv():
            pass

    #sync to arfcn
    def fbsb_req(self, arfcn):
        pack = osmol1(msgtype=1) / osmol1_fbsb_req(band_arfcn=arfcn)
        self.l1_send(pack)

        while True:
            p = self.l1_recv()
            if osmol1_fbsb_conf in p:
                if p.result == 0:
                    p2 = self.recv()
                    dbm = p2.signal_level - 110
                else:
                    dbm = -110
                print "Arfcn: %d result %3d rxlevel: %ddbm" % (arfcn, p.result, dbm)
                return p, dbm

    def dm_est_req(self, channel_type, timeslot, maio, hsn, training_sequence, ma, tch_mode=0, h=1):
        ma_pad = ma + [0] * (64-len(ma))
        est = osmol1_dm_est_req(
            link_id = 0,
            tsc=training_sequence,
            h = h,
            channel_type = channel_type,
            timeslot = timeslot,
            maio = maio,
            ma = ma_pad,
            n = len(ma),
            tch_mode = tch_mode,
            audio_mode = 5)

        pack = osmol1(msgtype=msgtype["DM_EST_REQ"]) / est
        print repr(pack)
        self.l1_send(pack)
            
    def rach_req(self, ra, combined=0, offset=0):
        rq = osmol1_rach_req(
            channel_type=0,
            timeslot=0,
            link_id=0,
            ra=ra,
            combined=combined,
            offset=offset)
        pack = osmol1(msgtype=msgtype["RACH_REQ"]) / rq
        #print repr(pack)
        self.l1_send(pack)

    def data_req(self, timeslot, channel_type, data):
        rq = osmol1_data_req(
            channel_type=0,
            timeslot=0,
            link_id=0)
        pack = osmol1(msgtype=msgtype["DATA_REQ"]) / rq
        self.l1_send(pack)

    def param_req(self, timing_advance, tx_power):
        pr = osmol1_par_req(
            channel_type=0,
            timeslot=0,
            link_id=0,
            ta=timing_advance,
            tx_power=tx_power)
        pack = osmol1(msgtype=msgtype["PARAM_REQ"]) / pr
        print repr(pack)
        self.l1_send(pack)

    def pm_req(self, arfcn_from, arfcn_to):
        pr = osmol1_pm_req(##
            arfcn_from=arfcn_from,
            arfcn_to=arfcn_to)
        pack = osmol1(msgtype=msgtype["PM_REQ"]) / pr
        self.l1_send(pack)

    def neigh_pm_req(self, arfcn_tn):
        padding = [0] * (64-len(arfcn_tn))
        pr = osmol1_neigh_pm_req(
            n=len(arfcn_tn),
            band_arfcn=map(lambda x:x[0], arfcn_tn) + padding,
            tn=map(lambda x:x[1], arfcn_tn) + padding)
        pack = osmol1(msgtype=msgtype["NEIGH_PM_REQ"]) / pr
        self.l1_send(pack)


    #receive data
    def recv(self):
        while True:
            p = self.l1_recv()
            if p.msgtype == 3:
                gsmtap_hdr = gsmtap.Gsmtap(
                    channel_type = channel_type2gsmtap(p.channel_type)[0],
                    timeslot = channel_type2gsmtap(p.channel_type)[1],
                    subslot = gsmtap.sdcch_subslot(p.channel_type, p.frame_nr),
                    frame_nr = p.frame_nr,
                    signal_level = p.rx_level,
                    snr = p.snr,
                    arfcn = p.arfcn,
                )
                data =  str(gsmtap_hdr / p[osmol1_data_ind].payload)
                self.gsmtap_sock.sendto(data, ("127.0.0.1", 4729))
                p = gsmtap.Gsmtap(data)
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

        n_bytes = 0
        start = time.time()
        while 1:
            readable,_,_ = select.select([conn], [], [], 0)
            if readable:
                l = struct.unpack("!H", conn.recv(2))[0]
                buff = conn.recv(l)
                n_bytes += len(buff)
                if self.proxy_process(buff,"pc->ms"):
                    self.l1_send(buff)

            readable,_,_ = select.select([self.sock], [], [], 0)
            if readable:
                buff = self.l1_recv(raw=True)
                n_bytes += len(buff)
                if self.proxy_process(buff, "ms->pc"):
                    l = struct.pack("!H", len(buff))
                    conn.send(l + str(buff))


            time.sleep(0.0001)
            #if time.time() - start > 1:
            #    print "rate: %f kbit/s" % (n_bytes*8/1e3)
            #    n_bytes = 0
            #    start = time.time()
                

    def proxy_process(self, pack, direction):
        p = osmol1(pack)
        skip = [
            msgtype["RESET_REQ"],
            msgtype["DATA_IND"],
            msgtype["SIM_REQ"],
            msgtype["SIM_CONF"],
            msgtype["NEIGH_PM_REQ"],
            msgtype["NEIGH_PM_IND"],
            msgtype["RESET_REQ"],
            msgtype["RESET_CONF"],
            #msgtype["FBSB_REQ"],
            msgtype["CCCH_MODE_REQ"],
            msgtype["PM_CONF"],
        ]

        if p.msgtype == msgtype["DATA_IND"] or p.msgtype == msgtype["DATA_REQ"]:
            gsmtap_hdr = gsmtap.Gsmtap(
                channel_type = channel_type2gsmtap(p.channel_type)[0],
                    timeslot = channel_type2gsmtap(p.channel_type)[1],
            )
            if p.msgtype == msgtype["DATA_IND"]:
                gsmtap_hdr.frame_nr = p.frame_nr
                subslot = gsmtap.sdcch_subslot(p.channel_type, p.frame_nr)
                gsmtap_hdr.arfcn = p.arfcn
                gsmtap_hdr.signal_level = p.rx_level
                data =  str(gsmtap_hdr / p[osmol1_data_ind].payload)
            else:
                gsmtap_hdr.uplink = 1
                data =  str(gsmtap_hdr / p[osmol1_data_req].payload)
                print len(p[osmol1_data_req].payload)

            self.gsmtap_sock.sendto(data, ("127.0.0.1", 4729))
            g = gsmtap.Gsmtap(data)
            try:
                gsmtap.process(g)
                print repr(g)
            except:
                pass
        #if p.msgtype in skip:
        #    return

        print direction, repr(p)
        return True

    # Layer 2
    def scan(self, arfcn_from, arfcn_to, threshold=-70):
        self.pm_req(arfcn_from, arfcn_to)
        arfcn_last = 0
        result = []
        while arfcn_last < arfcn_to:
            p = self.l1_recv()
            if osmol1_pm_conf in p:
                pm_conf = p.payload
                while pm_conf:
                    rxlevel = pm_conf.pm1-110
                    color = "\033[31m" if rxlevel < threshold else "\033[32m"
                    print "%sarfcn: %d rxlevel: %ddbm\033[39m" % (color, pm_conf.arfcn, pm_conf.pm1-110)
                    arfcn_last = pm_conf.arfcn
                    result += [(pm_conf.arfcn, rxlevel)]

                    pm_conf = pm_conf.payload

        return sorted(result, key=lambda x: x[1], reverse=True)

    def sync(self, arfcn_from, arfcn_to):
        self.reset()
        for arfcn, rxlevel in self.scan(arfcn_from, arfcn_to):
            self.reset()
            p,dbm = self.fbsb_req(arfcn)
            if p.result != 255:
                return arfcn, dbm

    def get_ca(self):
        while True:
            p = self.recv()
            if gsmtap.SystemInformationType1 in p:
                s1 = p[gsmtap.SystemInformationType1]
                ca = gsmtap.channelList2arfcn(s1.ChannelList)
                ca = sorted(ca)
                print "Cell Allocation: %s" % (str(ca))
                return ca

    def get_cell_id(self):
        while True:
            p = self.recv()
            if gsmtap.SystemInformationType3 in p:
                s3 = p[gsmtap.SystemInformationType3]
                print "Cell ID: %d" % s3.cell_id
                return s3.cell_id



if __name__ == "__main__":
    l1 = l1ctl("/tmp/osmocom_l2")
    l1.proxy("/tmp/osmocom_l2_proxy")

    #l1.fbsb_req(22)
    #
    #sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #while True:
    #    data = l1.recv()
    #    print repr(data)

