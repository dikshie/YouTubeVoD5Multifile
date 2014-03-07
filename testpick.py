#!/usr/bin/env python

import peer
import event 
import cdn
import cPickle as pickle

numpeer = 10000
cache_size = 1000.0 #100M
upload_bw = 1000.0 #100kbps
download_bw = 1000.0 #1Mbps = 1000Kbps

filename='cache_events-6jam-75600'
with open(filename, 'rb') as f:
    et=pickle.load(f)

print type(et), len(et)
for item in et:
    print item
f.close()
