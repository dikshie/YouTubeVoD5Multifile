#!/usr/bin/env python

#import scipy
import random
"""The simulation proceeds in rounds.  In each round there is an event."""

import peer
import event
import cdn
import math
import copy
import cPickle as pickle
from datetime import datetime

time_cur = 3600
cache_size = 1000.0 #100M
upload_bw = 1000.0 #100kbps
download_bw = 1000.0 #1Mbps = 1000Kbps
lamb = 1.2
event_list = event.Timeline()
#this_cdn = cdn.CDN(contents)
numpeer = 100000 
#skala = 183*24*3600 #1/2 tahun * 366 hari * 24 jam * 3600 detik
skala=30*24*3600
expected = 360 #360 peer per hour 
multiple_of = range(100000)
interval = (7200) 
counter = 0

vektor_viewcr={}
dict_for_resume={}
results_p = {}

TIMELINE_LENGTH = 24*3600


if __name__ == '__main__':
    #baca file dari catalog.pickle yng sebelumnya digenerate oleh catalog-generator
    #open catalog
    with open('catalog.pickle', 'rb') as handle:
        catalog = pickle.load(handle)
    handle.close()
    jumlahvideo = len(catalog)

    # generate peers
    this_cdn = cdn.CDN(catalog)
    peer_list = []
    for p in range(numpeer):
        np = peer.Peer(p, this_cdn, cache_size, upload_bw, download_bw)
        peer_list.append(np)
    this_cdn.set_peer_list(peer_list)
    

    def WeightedPick(d):
        r = random.uniform(0, sum(d.itervalues()))
        s = 0.0
        for k, w in d.iteritems():
            s += w
            if r < s: return k
        return k


    request_list_size = 0
    skala = int(skala)

    file_list = [ 'request_events-1b-'+str(TIMELINE_LENGTH*(i+1)) for i in range(skala/TIMELINE_LENGTH) ]
    print file_list

    
    for ev in range(skala):      
        tx = random.expovariate(expected) # exponential inter-arrival
        time_cur = time_cur + tx*expected #current time        
        actor = random.choice(peer_list)  # number of nodes
        #print 'actor: ', actor

        #pemilihan content_id yg bikin mumet
        if  time_cur >= multiple_of[0]*interval:
            selang=multiple_of[0]*interval
            #mulai hitung beta dan alpha utk tiap video
            for j in range(0,jumlahvideo):
                #hitung vektor viewcount dan dan viewrate utk tiap video
                #format vektor = {'video_id':video_id, 'view_count':viewcount, 'viewrate': viewrate}

                #ambil nilai terminus view count
                viewcterminus=catalog[j]['viewcounterminus']

                #hitung nilai cumulative view count scale ke detik
                view_count_t = catalog[j]['cdf'][selang] * viewcterminus

                #hitung nilai cumulative view count scale ke detik
                view_rate_t = catalog[j]['pdf'][selang] * viewcterminus

                if not vektor_viewcr.has_key(j):
                    #inisialisasi jika belum ada key
                    vektor_viewcr[j]={'video_id':j, 'view_count':[view_count_t], 'view_rate':[view_rate_t]}
                else:
                    #tambahkan sesudah memiliki key
                    vektor_viewcr[j]['video_id']=j
                    vektor_viewcr[j]['view_count'].append(view_count_t)
                    vektor_viewcr[j]['view_rate'].append(view_rate_t)

            for key2, value in vektor_viewcr.iteritems():
                cview=value['view_count'].pop()
                cview2=cview*7
                rview=value['view_rate'].pop()
                rview2=rview*3
                newvalue=cview2+rview2
                newvalue=int(newvalue)
                dict_for_resume[key2]=newvalue 
                #dict_for_resume2[key2]=rview
        
            p = WeightedPick(dict_for_resume)
            content_id = copy.deepcopy(p)
            #results_p[p] = results_p.get(p, 0) + 1
        #print counter , p 
        if time_cur > (interval)*(multiple_of[0]+1):
            #print i, waktu
            multiple_of.pop(0) 

        #content_id = random.randint(1,30) # requested file
    
        #event.request, time, actor, actor action, action parameters
        ev = event.Event(event.REQUEST, time_cur, actor, actor.request_to_cdn, [content_id, time_cur])
        event_list.append_event(ev)

        if (counter%TIMELINE_LENGTH)==TIMELINE_LENGTH-1:
            filename='request_events-1b-'+ str(counter+1)
            file_list.append(filename)
            with open(filename, 'wb') as f:
                event_list.marshall()
                pickle.dump(event_list, f)
            event_list.timeline = []
            print counter, str(datetime.now())

        counter+=1

    # dump the last timelines
    filename='request_events-1b-'+ str(counter)
    file_list.append(filename)
    with open(filename, 'wb') as f:
        event_list.marshall()
        pickle.dump(event_list, f)
    event_list.timeline = []
    print counter, str(datetime.now())
    #print len(catalog)
