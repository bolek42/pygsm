#Summary
The aim of this project will be to monitor active hopping channels on a BTS.


# Installation and Requirements
Install the following packages:

    -Osmocom-bb
    -Scapy
    -GNURadio
    -python2

# Experimental patches to Osmocom layer1
The scheduler in layer1/mframe\_sched.c calls the neighbour power measurement every 10 frames.
This can be modified to perform powermeasurements every frame, increasing performance.
Even though, there might be stability problems ;)
This will be further evaluated...


```c
/* Measurement for MF 51 C0 */
//static const struct mframe\_sched\_item mf\_neigh\_pm51\_c0t0[] = {
//  { .sched\_set = NEIGH\_PM   , .modulo = 51, .frame\_nr = 0 },
//  { .sched\_set = NEIGH\_PM   , .modulo = 51, .frame\_nr = 10 },
//  { .sched\_set = NEIGH\_PM   , .modulo = 51, .frame\_nr = 20 },
//  { .sched\_set = NEIGH\_PM   , .modulo = 51, .frame\_nr = 30 },
//  { .sched\_set = NEIGH\_PM   , .modulo = 51, .frame\_nr = 40 },
//  { .sched\_set = NULL }
//};
static const struct mframe\_sched\_item mf\_neigh\_pm51\_c0t0[] = {
    { .sched\_set = NEIGH\_PM   , .modulo = 1, .frame\_nr = 0 },
    { .sched_set = NULL }
};
```



## l1ctl.py
Osmocom BB Layer1 Implementation.
If called directly, a new socket file '/tmp/osmocom\_l2\_proxy' is created, that can be used instead of '/tmp/osmocom\_l2' with the Osmocom mobile app.
All exchanged layer 1 messages will be dumped to console.


## gsmtap.py
Implements some GSMTAP packets and allows to dissect them.
Currently it will only receive packets recieved on UDP 4729 and show informations on Immediate Assignments and Assignment commands.

## hopping.py
Experimental script for following hopping channels.

## pm.py
Experimental script for power measurements
