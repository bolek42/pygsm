#!/bin/bash

CA="120 115 109 106 75 55"
CA="55 120"
NSAMPLES=32000000

#############################################################

minARFCN=`echo $CA | awk '{print $1}'`
maxARFCN=`echo $CA | awk '{print $NF}'`

ARFCN_fc=$((($maxARFCN+$minARFCN)/2))

if [ $ARFCN_fc -gt 125 ]
then
  FC=$((1805200000 + 200000*$(($ARFCN_fc-512))))
else
  FC=$((935000000 + 200000*$ARFCN_fc))
fi

#Bandwidth in kHz
BW=$((($maxARFCN-$minARFCN+1)*200))

if [ $BW -gt 8000 ]
then
  SR=16000000
  NCHANNELS=125
  pfbDECIM=46
  totDECIM=184
elif [ $BW -gt 200 ]
then
  SR=10000000
  NCHANNELS=50
  pfbDECIM=17
  totDECIM=170
elif [ $BW -eq 200 ]
then
  SR=574712
  NCHANNELS=1
  pfbDECIM=1
  totDECIM=174
fi

echo "min_ARFCN: $minARFCN"
echo "max_ARFCN: $maxARFCN"
echo "Center ARFCN: "$ARFCN_fc
echo "Center frequency: $FC"khz
echo "Bandwidth: $BW" 
echo "Sampling rate: $SR" 
echo "Number of samples: $NSAMPLES"
echo "CA files: $CA_FILES"
echo "C0 ARFCN: $C0"
echo "C0 position: $c0POS"
echo "SR: $SR"
echo "NCHANNELS: $NCHANNELS"
echo "pfbDECIM: $pfbDECIM"
echo "totDECIM: $totDECIM"

uhd_rx_cfile -g 76 -f "$FC" --samp-rate="$SR" out/out.cf -N "$NSAMPLES"
./channelize.py --inputfile="out/out.cf" --arfcn="$ARFCN_fc" --srate="$SR" --decimation="$pfbDECIM" --nchannels="$NCHANNELS" --nsamples=$NSAMPLES

