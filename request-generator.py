#!/usr/bin/env python

#import scipy
import random
"""The simulation proceeds in rounds.  In each round there is an event."""

import peer
import event
import cdn
import math
import cPickle as pickle
from datetime import datetime

#scipy.random.seed(1024)

#random.seed(1)
contents = {
 1:[1,1000.0,3600],  2:[ 2,1000.0,3600], 3:[3,1000.0,3600],  4:[ 4,1000.0,3600], 5:[ 5,1000.0,3600], 6:[ 6,1000.0,3600], 7:[ 7,1000.0,3600], 8:[ 8,1000.0,3600],  
 9:[9,1000.0,3600], 10:[10,1000.0,3600],11:[11,500.0,1800], 12:[12,500.0,1800], 13:[13,500.0,1800], 14:[14,500.0,1800], 15:[15,500.0,1800], 16:[16,500.0,1800], 17:[17,500.0,1800], 18:[18,500.0,1800], 19:[19,500.0,1800], 20:[20,500.0,1800], 21:[21,400.0,1200], 22:[22,400.0,1200], 23:[23,400.0,1200], 24:[24,400.0,1200], 25:[25,400.0,1200], 26:[26,400.0,1200], 27:[27,400.0,1200], 28:[28,400.0,1200], 29:[29,400.0,1200], 30:[30,400.0,1200]     
} 

time_cur = 0
cache_size = 1000.0 #100M
upload_bw = 1000.0 #100kbps
download_bw = 1000.0 #1Mbps = 1000Kbps
lamb = 1.2
event_list = event.Timeline()
this_cdn = cdn.CDN(contents)
numpeer = 10000 
#skala = 183*24*3600 #1/2 tahun * 366 hari * 24 jam * 3600 detik
skala=30*24*3600
expected = 360 #360 peer per hour 
multiple_of = range(100000)
interval = 7200 
counter = 0

TIMELINE_LENGTH = 24*3600

if __name__ == '__main__':

    # generate peers
    peer_list = []
    for p in range(numpeer):
        np = peer.Peer(p, this_cdn, cache_size, upload_bw, download_bw)
        peer_list.append(np)
    this_cdn.set_peer_list(peer_list)
    
    print ('masuk generate request')


    # generate request events
    #request_events = shelve.open('request_events-3600-60')
    #for k in request_events:
    #    del request_events[k]
    #request_events.sync()
    #request_events['heads'] = [0]
    #request_events['0'] = []

    request_list_size = 0
    skala = int(skala)


    file_list = [ 'request_events-1bulan-'+str(TIMELINE_LENGTH*(i+1)) for i in range(skala/TIMELINE_LENGTH) ]
    print file_list

    
    for ev in range(skala):      
        tx = random.expovariate(expected) # exponential inter-arrival
        time_cur = time_cur + tx*expected#current time
        #block multi file
        #time_cur = round(time_cur, 5)
        actor = random.choice(peer_list) # number of nodes
        #print 'actor: ', actor
     
        content_id = random.randint(1,30) # requested file
    
        #event.request, time, actor, actor action, action parameters
        ev = event.Event(event.REQUEST, time_cur, actor, actor.request_to_cdn, [content_id, time_cur])
        event_list.append_event(ev)

        if (counter%TIMELINE_LENGTH)==TIMELINE_LENGTH-1:
            filename='request_events-1bulan-'+ str(counter+1)
            file_list.append(filename)
            with open(filename, 'wb') as f:
                event_list.marshall()
                pickle.dump(event_list, f)
            event_list.timeline = []
            print counter, str(datetime.now())

        counter+=1

    # dump the last timelines
    filename='request_events-1bulan-'+ str(counter)
    file_list.append(filename)
    with open(filename, 'wb') as f:
        event_list.marshall()
        pickle.dump(event_list, f)
    event_list.timeline = []
    print counter, str(datetime.now())
    
    """
    #raw_input('Enter')

    #print

    #event_timeline = event.Timeline()
    #for fn in file_list:
    #    with open(fn, 'rb') as f:
    #        et = pickle.load(f)
    #        et.unmarshall(peer_list)
    #        print et
    #        event_timeline.timeline += et.timeline

    #raw_input('Return')
    #print '-->' , req_head_list
    #print 'finished request, enter simulation main loop'
    #print 'time_cur akhir', time_cur


    def extend_event_list(filename):
        with open(filename, 'rb') as f:
            print 'LOAD', filename
            et = pickle.load(f)
            et.unmarshall(peer_list)
            event_list.extend_timeline(et)


    print 'masuk simulasi'

    extend_event_list(file_list.pop(0))

    #main loop; runs as long as there are events
    while event_list:
        next_event = event_list.get_next_event()

        if file_list and not event_list:
            extend_event_list(file_list.pop(0))

            #pass
        #print str(next_event)        
        new_events,cancelled_events = next_event.execute()
        
        for c in cancelled_events:
            if not c:
                continue
            event_list.cancel_event(c)
            #print '    CANCEL', c
            
        for n in new_events:
            try:
                while n.time > event_list.timeline[-1].time:
                    # load dari shelve kalau masih ada di shelve
                    if file_list:
                        extend_event_list(file_list.pop(0))
                    else:
                        break
                event_list.add_event(n)
                #print '   ADD', n
            except:
                pass
        
        ##print str(next_event)
        if (counter)>(multiple_of[0]+1)*interval:
            print counter
            multiple_of.pop(0)
        counter+=1 
    print 'finished simulation'
    """

        