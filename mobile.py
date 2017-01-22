from subprocess import Popen, PIPE, STDOUT
from multiprocessing import Process,Queue,cpu_count
import os
import telnetlib
import time
import sys

from l1ctl import *
from gsmtap import *

class mobile:
    def __init__(self):
        print "launch mobile"
        FNULL = open(os.devnull, 'rw')
        p = Popen(["mobile", "-i", "127.0.0.1"], stdout=FNULL, stdin=FNULL, stderr=FNULL)
        self.mobile_process = p

        print "connect to cli"
        while True:
            try:
                self.mobile_sock = telnetlib.Telnet("127.0.0.1",4247)
                break
            except:
                pass

        self.mobile_sock.write("enable\n")
        self.mobile_sock.read_until("OsmocomBB#")

        Process(target=self.gsmtap, args=[]).start()

    def shutdown(self):
        self.cmd("off")
        try:
            self.mobile_process.wait()
        except:
            os.kill(self.mobile_process.pid, 9)
        os.kill(os.getpid(), 9)

    def cmd(self, cmd):
        self.mobile_sock.write("%s\n" % cmd)
        ret = self.mobile_sock.read_until("OsmocomBB")
        ret += self.mobile_sock.read_until("#")
        return ret
        

    def stick_arfcn(self, arfcn):
        self.cmd("configure terminal")
        self.cmd("ms 1")
        self.cmd("stick %d" % arfcn)
        self.cmd("exit")
        self.cmd("exit")

    def wait_for_auth(self):
        while True:
            line = self.mobile_sock.read_until("\n")
            sys.stdout.write(line)
            if "On Network, normal service:" in line:
                return

    def call(self, nr):
        ret = self.cmd("call 1 %s" % nr)
        sys.stdout.write(ret)
        while True:
            line = self.mobile_sock.read_until("\n")
            sys.stdout.write(line)
            if "On Network, normal service:" in line or "No service" in line:
                return

    def gsmtap(self):
        port = 4729 #gsmtap
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", port))

        while 1:
            raw, addr = sock.recvfrom(1024)
            p = Gsmtap(raw)
            process(p)


    def proxy_process(self, pack, direction):
        p = osmol1(pack)

        if p.msgtype in (msgtype["NEIGH_PM_REQ"], msgtype["NEIGH_PM_IND"]):
            return False


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

            g = gsmtap.Gsmtap(data)
            gsmtap.process(g)


        return True

m = mobile()
try:
    m.stick_arfcn(int(sys.argv[1]))
    m.wait_for_auth()
    print m.cmd("show ms 1")
    
    m.call("015112793762")
    m.shutdown()
except:
    import traceback; traceback.print_exc()
    m.shutdown()
