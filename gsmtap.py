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
    "ACCH": 0x80,
    "SACCH8": 0x80}

gsm_channel_type = {
    0b00001: "Bm_ACCHs",
    0b00010: "Lm_ACCHs#0",
    0b00011: "Lm_ACCHs#1",
    0b00100: "SDCCH4_ACCH#0",
    0b00110: "SDCCH4_ACCH#1",
    0b00110: "SDCCH4_ACCH#2",
    0b00111: "SDCCH4_ACCH#3",
    0b01000: "SDCCH8_ACCH#0",
    0b01001: "SDCCH8_ACCH#1",
    0b01010: "SDCCH8_ACCH#2",
    0b01011: "SDCCH8_ACCH#3",
    0b01100: "SDCCH8_ACCH#4",
    0b01101: "SDCCH8_ACCH#5",
    0b01110: "SDCCH8_ACCH#6",
    0b01111: "SDCCH8_ACCH#7",
    0b10000: "BCCH",
    0b10001: "RACH",
    0b10010: "PCH_AGCH"}

def sdcch_subslot(channel_type, frame_nr):
    sdcch8=[0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,
            0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,-1,-1,-1,0,0,0,0,1,1,1,1,2,2,2,2,
            3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,4,4,4,4,5,5,5,5,6,6,6,6,
            7,7,7,7,-1,-1,-1]
    sdcch4=[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
            0,0,0,0,1,1,1,1,-1,-1,2,2,2,2,3,3,3,3,-1,-1,0,0,0,0,1,1,1,1,-1,-1,
            -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
            0,0,0,0,1,1,1,1,-1,-1,2,2,2,2,3,3,3,3,-1,-1,2,2,2,2,3,3,3,3,-1]

    if (channel_type ^ 0b01000) & 0b11000 == 0: #sdcch8
        return sdcch8[frame_nr%102]
    if (channel_type ^ 0b00100) & 0b11100 == 0: #sdcch4
        return sdcch4[frame_nr%102]
    return 0



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

class SystemInformationType1(Packet):
    fields_desc=[   ByteField("FormatIdentifier", 0),
                    FieldListField("ChannelList", None, ByteField("arfcn",0), count_from=lambda p: 15),
                    BitField("rach_retrans", 0x00, 2),
                    BitField("tx_offset", 0x00, 4),
                    BitField("cell_barr_access", 0x00, 1),
                    BitField("cell_reestablishment", 0x00, 1),
                    ShortField("acc", 0x00)]

#TODO add missing fields
class SystemInformationType3(Packet):
    fields_desc=[   ShortField("cell_id", 0x0000),
                    BitField("mcc2", 0x0, 4),
                    BitField("mcc1", 0x0, 4),
                    BitField("padding", 0xf, 4),
                    BitField("mcc3", 0x0, 4),
                    BitField("mnc2", 0x0, 4),
                    BitField("mnc1", 0x0, 4),
                    ShortField("lac", 0x0000)]


class PagingRequestType1(Packet):
    fields_desc=[   BitField("channel1", 0x00, 2),
                    BitField("channel2", 0x00, 2),
                    BitField("pageMode", 0x00, 4),
                    ]

def channelList2arfcn(cl):
    arfcns = []
    ca = 120
    for c in cl:
        for bit in range( 7,-1,-1):
            if (c >> bit) & 0x1 == 1:
                arfcns.append(ca - ( 7 - bit))
        ca -= 8

    return arfcns

class ImmediateAssignment(Packet):
    fields_desc=[   BitField("dedicated_or_tbf", 0x00, 4),
                    BitField("page_mode", 0x00, 4),
                    BitField("channel_type", 0x00, 5),
                    BitField("timeslot", 0x00, 3),
                    BitField("training_sequence", 0x00, 3),
                    BitField("hopping", 0x00, 1),
                    BitField("maio", 0x00, 6),
                    BitField("hsn", 0x00, 6),
                    ByteField("ra", 0x00),
                    BitField("t1", 0x00, 5),
                    BitField("t2", 0x00, 6),
                    BitField("t3", 0x00, 5),
                    ByteField("timing_advance", 0x00),
                    ByteField("ma_len", 0x00),
                    ByteField("ma", 0x00),
                    ]

bind_layers(Gsmtap, CCCH, channel_type=channel_type["CCCH"])
bind_layers(Gsmtap, CCCH, channel_type=channel_type["BCCH"])
bind_layers(Gsmtap, CCCH, channel_type=channel_type["PCH"])
bind_layers(CCCH, SystemInformationType1, type=0x19)
bind_layers(CCCH, SystemInformationType3, type=0x1b)
bind_layers(CCCH, PagingRequestType1, type=0x21)
bind_layers(CCCH, ImmediateAssignment, type=0x3f)


protocol_discriminator = {
    "CALL_CONTROLL": 0x3,
    "MOBILITY_MANAGEMENT": 0x5,
    "RADIO_RESOURCE_MANAGEMENT": 0x6,
    }

#Link Access Procedure
class LAPDM(Packet):
    fields_desc=[   BitField("padding", 0, 1),
                    BitField("lpd", 0, 2),
                    BitField("sapi", 0, 3),
                    BitField("cr", 1, 1), # 0
                    BitField("ea", 1, 1),
                    BitField("n_r", 0, 3),
                    BitField("padding", 0, 1),
                    BitField("n_s", 0, 3),
                    BitField("frame_type", 0, 1),
                    BitField("length", 0, 6),
                    BitField("m", 0, 1),
                    BitField("el", 1, 1),
                    BitField("skip_indicator", 1, 4),
                    BitEnumField("protocol_discriminator", 6, 4, protocol_discriminator),
                ]

#Mobility Management
mm_type = {
    "LOCATION_UPDATE_REQUEST": 0x8,
    }
class MobilityManagement(Packet):
    fields_desc=[   BitField("sequence", 0, 2),
                    BitField("type", 0, 6),
                ]
bind_layers(LAPDM, MobilityManagement, protocol_discriminator=protocol_discriminator["MOBILITY_MANAGEMENT"])

#XXX Incomplete
class LocationUpdateRequest(Packet):
    fields_desc=[   BitField("spare", 0, 1),
                    BitField("cipher_key_sequence", 0, 3),

                    BitField("follow_on_request", 0, 1),
                    BitField("spare", 0, 1),
                    BitField("updateing_type", 2, 2), #imsi attach

                    #location area information
                    BitField("mcc3", 0x0, 4),
                    BitField("mnc2", 0x0, 4),
                    BitField("mnc1", 0x0, 4),
                    ShortField("lac", 0x0000),

                    ByteField("mobile_station_classmark", 0x23),
                ]


#Radio Resource Management
rss_type = {
    "ASSIGNMENT_COMMAND": 0x2e,
    "CIPHERING_MODE_COMMAND": 0x35,
    }

class RadioRessourceManagement(Packet):
    fields_desc=[   ByteEnumField("type", None, rss_type)]

bind_layers(LAPDM, RadioRessourceManagement, protocol_discriminator=protocol_discriminator["RADIO_RESOURCE_MANAGEMENT"])

class AssignmentCommand(Packet):
    fields_desc=[   BitField("channel_type", 0, 5),
                    BitField("timeslot", 0, 3),
                    BitField("training_sequence", 4, 3),
                    BitField("hopping", 1, 1),
                    BitField("maio", 0x00, 6),
                    BitField("hsn", 0x00, 6),
                    BitField("powerCommand", 0x00, 8),
                    BitField("elementID", 0x00, 8),
                    BitField("length", 0x00, 8),
                    BitField("formatID", 0x00, 8),
                    FieldListField("ChannelList", None, ByteField("arfcn",0), count_from=lambda p: 15),
                ]
    
bind_layers(RadioRessourceManagement, AssignmentCommand, type=rss_type["ASSIGNMENT_COMMAND"])
                    

bind_layers(Gsmtap, LAPDM, channel_type=channel_type["SDCCH8"])


def process(p):
    arfcn = p[Gsmtap].arfcn
    if LAPDM in p:
        pass
        #print repr(p[LAPDM])

    if SystemInformationType1 in p and False:
        s1 = p[SystemInformationType1]
        arfcns = channelList2arfcn(s1.ChannelList)
        print "SystemInformation1: \tArfcn %d Cell Allocation %s" % (arfcn, str(arfcns))

    if ImmediateAssignment in p:
        ia = p[ImmediateAssignment]
        print "Immediate Assignment:\tArfcn: %d Hopping: %d Maio: %d HSN: %d Channel: %s Timeslot %d Ma: %s" % (arfcn, ia.hopping, ia.maio, ia.hsn, gsm_channel_type[ia.channel_type], ia.timeslot, bin(ia.ma)[2:])

    if AssignmentCommand in p:
        ac = p[AssignmentCommand]
        if ac.hopping:
            ma = channelList2arfcn(ac.ChannelList)
        else:
            ma = [int(ac.hsn + ((ac.maio & 0xf)<<6))]
        if len(ma) > 8:
            print "error, mobile allocation too long"
            return
        print "Assignment Command:\tArfcn: %d Maio: %d HSN: %d Channel: %s Timeslot: %d Hopping: %d Ma: %s" % (arfcn, ac.maio, ac.hsn, gsm_channel_type[ac.channel_type], ac.timeslot, ac.hopping, ma)


if __name__ == "__main__":
    import sys
    from binascii import *
    if len(sys.argv) == 1:
        port = 4729 #gsmtap
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", port))

        while 1:
            raw, addr = sock.recvfrom(1024)
            print raw
            p = Gsmtap(raw)
            try:
                process(p)
            except:
                pass
    else:
        bind_layers(UDP, Gsmtap, dport=4729)
        for pack in rdpcap(sys.argv[1]):
            if Gsmtap in pack:
                p = Gsmtap(str(pack[Gsmtap]))
                process(p)
                



#l1 = l1ctl("/tmp/osmocom_l2")
#l1.fbsb_req(22)
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
