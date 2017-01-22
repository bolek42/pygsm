import sys
from l1ctl import *
from gsmtap import *
from random import *
import time
from random import shuffle
from hsn import *

def pm2fn(pm_ind):
    fn = 0
    pm_ind = p.payload
    for i in xrange(4):
        fn |= pm_ind.pm2 << (i*8)
        pm_ind = pm_ind.payload

    return fn

l1 = l1ctl("/tmp/osmocom_l2")
l1.reset()
time.sleep(0.1)

if False:
    arfcn = int(sys.argv[1])
    arfcn_tn = [(arfcn, 0)]
    for i in xrange(23):
        arfcn_tn += [(randrange(1,4),randrange(8))]

    shuffle(arfcn_tn)
    l1.reset()
    l1.neigh_pm_req(arfcn_tn)
    l1.neigh_pm_req(arfcn_tn)
    print arfcn_tn
    fn = t = 0
    while True:
        p = l1.l1_recv()
        if osmol1_neigh_pm_ind in p:
            pm_ind = p.payload
            print arfcn, pm2fn(pm_ind) - fn, len(arfcn_tn)
            print time.time() - t, (time.time() - t) / len(arfcn_tn)
            t = time.time()
            fn = pm2fn(pm_ind)
            while pm_ind:
                rxlevel = pm_ind.pm1-110
                if pm_ind.arfcn == arfcn:
                    color = "\033[33m" if rxlevel < -70 else "\033[32m"
                else:
                    color = "\033[31m" if rxlevel < -70 else "\033[32m"
                print color,rxlevel,pm_ind.arfcn, pm_ind.tn, "\033[39m:",
                pm_ind = pm_ind.payload
            print ""

#sync to arfcn
if len(sys.argv) == 1:
    arfcn, rxlevel = l1.sync(1, 124)
else:
    arfcn = int(sys.argv[1])
    l1.fbsb_req(arfcn)

#get ca list
ca = l1.get_ca()
cell_id = l1.get_cell_id()
arfcn_tn = []
for ch in ca:
    for i in xrange(8):
        arfcn_tn += [(ch,i)]

#get hsn
l1.rach_req(1, offset=7)
while True:
    p = l1.recv()
    if ImmediateAssignment in p:
        hsn = p[ImmediateAssignment].hsn
        break

l1.reset()
#time.sleep(0.1)
#l1.neigh_pm_req(arfcn_tn)
l1.neigh_pm_req(arfcn_tn)

offset = int(sys.argv[2])

ma = map(int, sys.argv[3:])


chan = {(ch, t): 0 for ch in ca for t in xrange(8)}
hop  = {(maio, t): 0 for maio in xrange(len(ma)) for t in xrange(8)}

j = 0
t = time.time()
print "\x1b[2J" #clear console
while True:
    print "\x1b[0;0H"

    #fetch results
    p = l1.l1_recv()
    if osmol1_neigh_pm_ind not in p:
        continue

    fn = 0
    pm_ind = p.payload
    for i in xrange(4):
        fn |= pm_ind.pm2 << (i*8)
        pm_ind = pm_ind.payload

    print time.time() - t, (time.time() - t) / len(arfcn_tn)
    t = time.time()
    pm_ind = p.payload

    i = 0
    while pm_ind:
        rxlevel = pm_ind.pm1-110
        ch = pm_ind.arfcn
        tn = pm_ind.tn
        ch, tn = arfcn_tn[(i + offset) % len(arfcn_tn)]
        for maio in xrange(len(ma)):
            if tn != 0:
                c = hsn_generator(fn + i - 1, hsn, maio, ma)
            else:
                c = hsn_generator(fn + i - 1, hsn, maio, filter(lambda x: x!=arfcn, ma))
            if c  == ch and c != arfcn:
                hop[(maio,tn)] = rxlevel
                break

        chan[(ch,tn)] = rxlevel
        i += 1

        pm_ind = pm_ind.payload
   
    print "cell: %d hsn = %d ma = %s fn = %d" % (cell_id, hsn, str(ma), fn)
   
    #print channel matrix
    print "\t\t",
    for tn in xrange(8):
        print "tn=%d\t\t" % tn,
    print ""
    for c in ca:
        print "channel %d:\t" % c,
        for tn in xrange(8):
            rxlevel =  chan[(c,tn)]
            color = "\033[31m" if rxlevel < -70 else "\033[32m"
            print "%s%4ddbm \033[39m\t" % (color, rxlevel), 
        print ""
    print ""


    #print hopping matrix
    print "\t\t",
    for tn in xrange(8):
        print "tn=%d\t\t" % tn,
    print ""
    for maio in xrange(len(ma)):
        print "maio %d:   \t" % maio,
        for tn in xrange(8):
            rxlevel =  hop[(maio,tn)]
            color = "\033[31m" if rxlevel < -70 else "\033[32m"
            print "%s%4ddbm \033[39m\t" % (color, rxlevel), 
        print ""

