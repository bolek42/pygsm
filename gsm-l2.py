import socket
import optparse

def hexdump( data):
    for c in data:
        print "%02x" % ord( c),
    print ""

class bcch:
    def __init__( self, data):
        self.data = data
        self.hlen = ord(data[0])
        self.pd = pd = ord(data[1]) #protocol discriminator
        self.mt = mt = ord(data[2]) #message types
        self.cell_allocation = []

        self.process()

    def process( self):
        if self.pd == 0x06: #usual package
            if self.mt == 0x19: #system information type 1
                self.system_info_1( data[3:])

            if self.mt == 0x3f: #immediate assignment
                self.immediate_assignment( data[3:])

            if self.mt == 0x21: #paging request type 1
                pass

            if self.mt == 0x22: #paging request type 2
                self.pm = data[3] #paging mode
                self.cn = data[4] #channel needed

                for i in range( 3):
                    tmsi_opt = data[4 + 6*i: 4 + 6*i + 1]
                    tmsi = data[4 + 6*i + 2: 4 + 6*i + 6]
                    #hexdump( tmsi)

                #hexdump( self.data)
        else:
            #print hex( self.pd)
            pass

    def system_info_1( self, data):
        format_id = ord( data[0])

        if format_id == 0: #bitmask 0
            ca = 120
            i = 1
            while ca > 0:
                b = ord( data[i])
                for bit in range( 7,-1,-1):
                    if (b >> bit) & 0x1 == 1:
                        self.cell_allocation.append( ca - ( 7 - bit))

                i += 1
                ca -= 8
            #print "CA:", self.cell_allocation

    def immediate_assignment( self, data):
        return
        hexdump(data)
        self.page_mode = ord( data[0]) & 0x0f

        print "got assignment"
        if ord(data[0]) & 0x10:
            #l2_RRimmediateAssTBFC()
            print "fooo"
            pass
        else:
            #channel description
            self.arcfn = ord( data[5])
            print self.arcfn

            if ord( data[0]) & 0x10:
                print "hopping channel"
            else:
                print "non hopping"


parser = optparse.OptionParser()
parser.add_option('--ca', action="store_true", default=False, help="show cell allocatoions")
(options, args) = parser.parse_args ()

port = 4729 #gsmtap
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("127.0.0.1", port))

while 1:
    raw, addr = sock.recvfrom(1024)
    gsmtap_len = ord(raw[1]) * 4
    gsmtap = raw[0:gsmtap_len-1]
    data = raw[gsmtap_len:]
    pack = bcch( data)
