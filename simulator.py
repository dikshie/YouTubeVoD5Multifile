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
import copy


#contents = {
#1:[1,1000.0,3600],  2:[ 2,1000.0,3600], 3:[3,1000.0,3600],  4:[ 4,1000.0,3600], 5:[ 5,1000.0,3600], 6:[ 6,1000.0,3600], 7:[ 7,1000.0,3600], 8:[ 8,1000.0,3600],  
#9:[#9,1000.0,3600], 10:[10,1000.0,3600],11:[11,500.0,1800], 12:[12,500.0,1800], 13:[13,500.0,1800], 14:[14,500.0,1800], 15:[15,500.0,1800], 16:[16,500.0,1800], 17:[17,500.0,1800], 18:[18,500.0,1800], 19:[19,500.0,1800], 20:[20,500.0,1800], 21:[21,400.0,1200], 22:[22,400.0,1200], 23:[23,400.0,1200], 24:[24,400.0,1200], 25:[25,400.0,1200], 26:[26,400.0,1200], 27:[27,400.0,1200], 28:[28,400.0,1200], 29:[29,400.0,1200], 30:[30,400.0,1200]     
#} 

time_cur = 3600*5 
cache_size = 1000.0 #100M
upload_bw = 1000.0 #100kbps
download_bw = 1000.0 #1Mbps = 1000Kbps
lamb = 1.2
event_list = event.Timeline()
numpeer = 100000 
#skala = 183*24*3600 #1/2 tahun * 366 hari * 24 jam * 3600 detik
skala=2*24*3600
expected = 360 #360 peer per hour 
multiple_of = range(100000)
interval = (2*3600) 
counter = 0

TIMELINE_LENGTH = 1*3600

if __name__ == '__main__':

    skala = int(skala)

    #buka file catalog konversi ke format lama
    with open('catalog.pickle', 'rb') as handle:
        catalog = pickle.load(handle)
    handle.close()
    jumlahvideo = len(catalog)

    #format baru:
    #catalog[video_id]={'video_id':video_id, 'uploaded':start, 'size':size, 'viewcounterminus':terminus, 'alpha':alpha_ , 'beta':beta_, 'pdf':{}, 'cdf':{} 
    #print catalog[0]['uploaded'], catalog[0]['size']
    #contoh: {1: [1, 34.433471105806156, 2586.0, 3600.0] }
    #format lama:
    #{videoi-d]:[video-id,size,cache]}
    contents={}
    for key,value in catalog.iteritems():
        contents[key]=[ key, value['uploaded'], float(value['size']), 3600.0 ]
    #print key, value['uploaded'], value['size']
    #contoh: {1: [1, 34.433471105806156, 258.0, 3600.0] }

    #inisialisasi kelas CDN
    this_cdn = cdn.CDN(contents)


    # generate peers
    peer_list = []
    for p in range(numpeer):
        np = peer.Peer(p, this_cdn, cache_size, upload_bw, download_bw)
        peer_list.append(np)
    this_cdn.set_peer_list(peer_list)

    file_list = [ 'request_events-1t-'+str(TIMELINE_LENGTH*(i+1)) for i in range(skala/TIMELINE_LENGTH) ]
    print file_list
    
    def extend_event_list(filename):
        with open(filename, 'rb') as f:
            print 'LOAD', filename
            et = pickle.load(f)
            et.unmarshall(peer_list)
            event_list.extend_timeline(et)

    #file utk menyimpan cancelled events:
    #f_cancel_time = open('cancelevent-time.pickle', 'wb')
    #f_cancel_actor = open('cancelevent-actor.pickle', 'wb')


    print 'masuk simulasi'
    extend_event_list(file_list.pop(0))


    file_list2 = [ 'cancel_events-1t-'+str(TIMELINE_LENGTH*(i+1)) for i in range(skala/TIMELINE_LENGTH) ]
    print file_list2

    file_list3 = [ 'reqtopeer_events-1t-'+str(TIMELINE_LENGTH*(i+1)) for i in range(skala/TIMELINE_LENGTH) ]
    print file_list3

    file_list4 = [ 'cache_events-1t-'+str(TIMELINE_LENGTH*(i+1)) for i in range(skala/TIMELINE_LENGTH) ]
    print file_list4

    file_list5 = [ 'cache_extend_events-1t-'+str(TIMELINE_LENGTH*(i+1)) for i in range(skala/TIMELINE_LENGTH) ]
    print file_list5

    file_list6 = [ 'expire_events-1t-'+str(TIMELINE_LENGTH*(i+1)) for i in range(skala/TIMELINE_LENGTH) ]
    print file_list6

    time_list_c = []
    time_list_c3 = []
    time_list_c4 = []
    time_list_c5 = []
    time_list_c6 = []
    
    #main loop; runs as long as there are events
    while event_list:
        next_event = event_list.get_next_event()

        if file_list and not event_list:
            extend_event_list(file_list.pop(0))

            
        #print str(next_event)        
        new_events,cancelled_events = next_event.execute()
        

        for c in cancelled_events:
            if not c:
                continue
            event_list.cancel_event(c)
            time_list_c.append(( c.time, str(c.actor) , c.type, c.action_params[0]))

            if (counter%TIMELINE_LENGTH)==TIMELINE_LENGTH-1:
                #print 'masuk'
                filename2='cancel_events-1t-'+ str(counter+1)
                file_list2.append(filename2)

                #old expire event/dihapus/cancel
                with open(filename2, 'wb') as f2:
                    #time_list_c2.marshall()
                    pickle.dump(time_list_c, f2)
                    #pickle.dump(time_list_c2, f2)
                time_list_c = []
                #print counter, str(datetime.now())
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
                #print 'panjang event_list', len(event_list.timeline)
                #print event_list.timeline
                #print '   ADD', n
            except:
                pass
        
        if next_event.action.__name__ == 'request_to_peer':
            time_list_c3.append(( next_event.time, str(next_event.actor) , next_event.type, next_event.action_params[0]))
        
        if next_event.action.__name__ == 'cache_content':
            time_list_c4.append(( next_event.time, str(next_event.actor) , next_event.type, next_event.action_params[0]))
         
        #new expire event/diperpanjang
        if next_event.action.__name__ == 'remove_content_extend':  
            time_list_c5.append(( next_event.time, str(next_event.actor) , next_event.type, next_event.action_params[0]))
        
        #origin expire event/expire asli
        if next_event.action.__name__ == 'remove_content':  
            time_list_c6.append(( next_event.time, str(next_event.actor) , next_event.type, next_event.action_params[0]))

        if (counter%TIMELINE_LENGTH)==TIMELINE_LENGTH-1:
                #request to peer
                filename3='reqtopeer_events-1t-'+ str(counter+1)
                file_list3.append(filename3)
                with open(filename3, 'wb') as f3:             
                    pickle.dump(time_list_c3,f3)
                time_list_c3 = []

                #cache event
                filename4='cache_events-1t-'+ str(counter+1)
                file_list4.append(filename4)
                with open(filename4, 'wb') as f4:             
                    pickle.dump(time_list_c4,f4)
                time_list_c4 = []

                #cache extend/expire extend dari new_expire_event
                filename5='cache_extend_events-1t-'+ str(counter+1)
                file_list5.append(filename5)
                with open(filename5, 'wb') as f5:             
                    pickle.dump(time_list_c5,f5)
                time_list_c5 = []

                #expire event original
                filename6='expire_events-1t-'+ str(counter+1)
                file_list6.append(filename6)
                with open(filename6, 'wb') as f6:             
                    pickle.dump(time_list_c6,f6)
                time_list_c6 = []

        ##print str(next_event)
        if (counter)>(multiple_of[0]+1)*interval:
            print counter, str(datetime.now())
            multiple_of.pop(0)
        counter+=1 

    # dump the last timelines
    if next_event.action.__name__ == 'request_to_peer':
        filename3='reqtopeer_events-1t-'+ str(counter)
        file_list3.append(filename3)
        time_list_c3.append(( next_event.time, str(next_event.actor) , next_event.type, next_event.action_params[0]))
        with open(filename3, 'wb') as f3:
            pickle.dump(time_list_c3, f3)
        time_list_c3 = []

    if next_event.action.__name__ == 'cache_content':
        filename4='cache_events-1t-'+ str(counter)
        file_list4.append(filename4)
        time_list_c4.append(( next_event.time, str(next_event.actor) , next_event.type, next_event.action_params[0]))
        with open(filename4, 'wb') as f4:
             pickle.dump(time_list_c4, f4) 
        time_list_c4 = []

    if next_event.action.__name__ == 'remove_content_extend':
        filename5='cache_extend_events-1t-'+ str(counter)
        file_list5.append(filename5)
        time_list_c5.append(( next_event.time, str(next_event.actor) , next_event.type, next_event.action_params[0]))
        with open(filename5, 'wb') as f5:
             pickle.dump(time_list_c5, f5) 
        time_list_c5 = []

    if next_event.action.__name__ == 'remove_content':
        filename6='expire_events-1t-'+ str(counter)
        file_list6.append(filename6)
        time_list_c6.append(( next_event.time, str(next_event.actor) , next_event.type, next_event.action_params[0]))
        with open(filename6, 'wb') as f6:
             pickle.dump(time_list_c6, f6) 
        time_list_c6 = []

    #dump the last timelines for cancelled events:
    if cancelled_events:
        time_list_c.append(( cancelled_events.time, str(cancelled_events.actor) , cancelled_events.type, cancelled_events.action_params[0]))
        filename2='cancel_events-1t-'+ str(counter+1)
        file_list2.append(filename2)
        with open(filename2, 'wb') as f2:
            pickle.dump(time_list_c, f2)
        time_list_c = []
    else:
        filename2='cancel_events-1t-'+ str(counter+1)
        file_list2.append(filename2)
        with open(filename2, 'wb') as f2:
            pickle.dump(time_list_c, f2)
        time_list_c = []





    #print counter, str(datetime.now())

    print 'finished simulation'
        