from scapy.all import *

channel_type = {
    "UNKNOWN": 0x00,
    "BCCH": 0x01,
    "CCCH": 0x02,
    "RACH": 0x03,
    "AGCH": 0x04,
    "PCH": 0x05,
    "SDCCH": 0x06,
    "SDCCH4": 0x07,
    "SDCCH8": 0x08,
    "TCH_F": 0x09,
    "TCH_H": 0x0a,
    "CBCH51": 0x0b,
    "CBCH52": 0x0c,
    "PDCH": 0x0d,
    "PTCCH": 0x0e,
    "PACCH": 0x0f,
    "ACCH": 0x80}



class Gsmtap(Packet):
    fields_desc=[   ByteField("version", 2),
                    ByteField("hdr_len", 4),
                    ByteField("payload_type" , 1),
                    ByteField("timeslot" , 0),
                    BitField("padding", 0x00, 1),
                    BitField("uplink", 0x00, 1),
                    BitField("arfcn", 0x00, 14),
                    ByteField("signal_level" , 0),
                    ByteField("snr" , 0),
                    IntField("frame_nr" , 0),
                    ByteEnumField("channel_type" , 1, channel_type),
                    ByteField("antenna_nr" , 0),
                    ByteField("subslot" , 0),
                    ByteField("padding" , 0),
    ]


class CCCH(Packet):
    fields_desc=[   XByteField("pseudo_len", 5),
                    XByteField("protocol_discriminator", 3) ,
                    XByteField("type" , 1)]

class PagingRequestType1(Packet):
    fields_desc=[   BitField("channel1", 0x00, 2),
                    BitField("channel2", 0x00, 2),
                    BitField("pageMode", 0x00, 4),
                    ]

class ImmediateAssignment(Packet):
    fields_desc=[   BitField("dedicated_or_tbf", 0x00, 4),
                    BitField("page_mode", 0x00, 4),
                    BitField("channel_type", 0x00, 5),
                    BitField("timeslot", 0x00, 3),
                    BitField("padding", 0x00, 1),
                    BitField("training_sequence", 0x00, 3),
                    BitField("maio", 0x00, 6),
                    BitField("hsn", 0x00, 6),
                    ]


bind_layers(Gsmtap, CCCH, channel_type=channel_type["CCCH"])
bind_layers(Gsmtap, CCCH, channel_type=channel_type["BCCH"])
bind_layers(Gsmtap, CCCH, channel_type=channel_type["PCH"])
bind_layers(CCCH, PagingRequestType1, type=0x21)
bind_layers(CCCH, ImmediateAssignment, type=0x3f)

if __name__ == "__main__":
    port = 4729 #gsmtap
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", port))

    while 1:
        raw, addr = sock.recvfrom(1024)
        p = Gsmtap(raw)
        print repr(p)
        if ImmediateAssignment in p:
            #print repr(p)
            ia = p[ImmediateAssignment]
            print "Maio: %d HSN: %d Timeslot %d" % (ia.maio, ia.hsn, ia.timeslot)


#l1 = l1ctl("/tmp/osmocom_l2")
#l1.set_arfcn(22)
#
#sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#while True:
#    #convert to gsmtap
#    p = l1.recv()
#    gsmtap_hdr = Gsmtap(
#        frame_nr = p.frame_nr,
#        signal_level = p.rx_level,
#        arfcn = p.arfcn,
#    )
#    data =  str(gsmtap_hdr / p[osmol1_data].payload)
#    sock.sendto(data, ("127.0.0.1", 4729))
#
#    p = Gsmtap(data)
#    if ImmediateAssignment in p:
#        #print repr(p)
#        ia = p[ImmediateAssignment]
#        print "Maio: %d HSN: %d Timeslot %d" % (ia.maio, ia.hsn, ia.timeslot)
