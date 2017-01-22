#Summary
The aim of this project will be to monitor active hopping channels on a BTS.

## channel\_monitor.py arfcn
This script uses the patched firmware to perform fast powermeasurements of the channels allocated by the cell.
It determines the HSN and shows the power level of all hopping and non hopping channels.
Per channel in the cell allocation, 36ms are needed for one measurement.

# Installation and Requirements
Install the following packages:

    -Osmocom-bb
    -Scapy
    -python2

# Experimental patches to Osmocom layer1 (osmocom-bb.patch)
The scheduler in layer1/mframe\_sched.c calls the neighbour cell discovery every 10th frames.
This was tuned to perform one measurement per frame.
Even though some further patches are required.


## l1ctl.py
Osmocom BB Layer1 Implementation.
If called directly, a new socket file '/tmp/osmocom\_l2\_proxy' is created, that can be used instead of '/tmp/osmocom\_l2' with the Osmocom mobile app.
All exchanged layer 1 messages will be dumped to console.

## gsmtap.py
Implements some GSMTAP packets and allows to dissect them.
Currently it will only receive packets recieved on UDP 4729 and show informations on Immediate Assignments and Assignment commands.
This code is really ugly...just for parsing some GSM messages.

## mobile.py
Dirty python wrapper for osmocom-bb cli interface

## hsn.py
The GSM hopping sequence generator

## hopping.py
Experimental script for following hopping channels.

## jammer.py
Experimental not tested yet..
