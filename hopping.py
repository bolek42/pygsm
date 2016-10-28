import sys
from l1ctl import *
from gsmtap import *
from random import *

def scan(l1):
    for arfcn in xrange(128):
        l1.reset()
        p,dbm = l1.fbsb_req(arfcn)
        if p.result == 0 and dbm > -70:
            return arfcn

l1 = l1ctl("/tmp/osmocom_l2")

#sync to cell
if len(sys.argv) == 1:
    arfcn = scan(l1)
else:
    arfcn = int(sys.argv[1])
    l1.fbsb_req(arfcn)

while True:
    p = l1.recv()
    if SystemInformationType1 in p:
        s1 = p[SystemInformationType1]
        arfcns = channelList2arfcn(s1.ChannelList)
        arfcns = sorted(arfcns)
        print "Cell Allocation: %s" % (str(arfcns))
        break


l1.param_req(0, 5)
l1.rach_req(1, offset=7)

#follow immediate assignment
f = open("/tmp/rxlevel.csv","w")
sync = 0
while True:
    p = l1.recv()
    if p.uplink == 0:
        f.write("%d, %d\n" % (p.frame_nr, p.signal_level - 110))
        f.flush()

    if ImmediateAssignment in p:
        process(p)
        ia = p[ImmediateAssignment]
        if "SDCCH" not in gsm_channel_type[ia.channel_type]:
            continue

        if sync > 0:
            continue

        sync = time.time()
        l1.reset(2)
        #l1.param_req(ia.timing_advance, 5)

        ma = []
        for i in xrange(len(arfcns)):
            if 1<<i & ia.ma:
                ma += [arfcns[i]]

        l1.dm_est_req(ia.channel_type, ia.timeslot, ia.maio, ia.hsn, ia.training_sequence, ma)

    if sync > 0 and time.time() - sync > 10:
        sync = 0
        print "return on ccch"
        while l1.fbsb_req(arfcn)[1] == -110:
            pass

    
