import sys
from l1ctl import *
from gsmtap import *
from random import *

l1 = l1ctl("/tmp/osmocom_l2")

#sync to cell
if len(sys.argv) == 1:
    arfcn, rxlevel = l1.sync(1, 124)
else:
    arfcn = int(sys.argv[1])
    l1.fbsb_req(arfcn)

arfcns = l1.get_ca()


#l1.param_req(0, 5)
#l1.rach_req(1, offset=7)

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

    if  sync > 0 and (p.signal_level - 110) > -75:
        sync = time.time()

    if sync > 0 and time.time() - sync > 10:
        sync = 0
        print "return on ccch"
        while l1.fbsb_req(arfcn)[1] == -110:
            pass

    
