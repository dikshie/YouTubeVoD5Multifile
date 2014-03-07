#!/usr/bin/env python

import random

class CDN(object):

    def __init__(self, catalog):
        self.type = 'CDN'
        self.upload_bandwidth = 0
        self.peer_list = None
        self.content_catalog = catalog
        self.peer_tracking = dict()
        self.video_tracking_time_requested = dict()
        self.video_tracking_number_requested = dict()
        self.cdnhitcounter = 0
        self.peerhitcounter = 0
        self.peertraffic = 0
        self.cdntraffic = 0
        
    def set_peer_list(self, peer_list):
        self.peer_list = peer_list
        
    def get_peer_from_id(self, id):
        for p in self.peer_list:
            if p.id == id:
                return p
        else:
            return None

    def get_number_requested_video(self, content_id):
        """
        ambil jumlah video yng telah di request
        """
        #print self.video_tracking_number_requested
        return self.video_tracking_number_requested[content_id]



    def get_video_last_time_requested(self, content_id):
        """
        ambil waktu terakhir video direquest
        """
        return self.video_tracking_time_requested[content_id]



    def get_content(self, peer_id, content_id, time_cur):
        """
        reply dengan content atau redirect
        """
        this_content=self.content_catalog[content_id]
        tracked_peer = self.get_peer_tracking(content_id)

        #rekam waktu video direquested
        self.video_tracking_time_requested[content_id]=time_cur

        #results_p[p] = results_p.get(p, 0) + 1
        self.video_tracking_number_requested[content_id] = self.video_tracking_number_requested.get(content_id,0)+1
        #print self.video_tracking_number_requested
        

        #peer excesive tracking
        #{peer_id: {video_id:[time_1, time_2], video_id: [time_1, time_2] , dst nya  }

        if tracked_peer:
            #print 'tracked_peer', tracked_peer , 'content_id', content_id
            #print 'p'
            self.peerhitcounter += 1
            return [None, tracked_peer]
            
        #jika content tidak ada di peer (None) maka kembalikan langsung dari CDN.
        else:
            #print 'cdnhit', self.cdnhitcounter
            self.cdnhitcounter += 1
            return [this_content, None]
    
        
    def receive_report_from_peer(self, peer_id, content_id, type):
        """
        report to cdn (model baru)
        type = CACHE, REMOVE_CACHE, UPLOADING, IDLE
        
        peer_tracking adalah dictionary dengan peer_id sebagai key, dan tiap value adalah dictionary dengan key peer_id, status, dan cache_content
        """
        
        if not self.peer_tracking.has_key(peer_id):
            self.peer_tracking[peer_id] = {'peer_id':peer_id, 'status':'IDLE', 'cache_content':{}}
            
        if type == 'CACHE':
            self.peer_tracking[peer_id]['cache_content'][content_id] = 1
            
        if type == 'REMOVE_CACHE':
            #print 'cdn', peer_id, content_id
            del self.peer_tracking[peer_id]['cache_content'][content_id]
            
        if type == 'UPLOADING':
            self.peer_tracking[peer_id]['status'] = 'UPLOADING'
            
        if type == 'IDLE':
            self.peer_tracking[peer_id]['status'] = 'IDLE'
        
        #sementara utk unittest
        #return self.peer_tracking
    
    
    def get_peer_tracking(self, content_id):
        """
        CDN harus punya catatan peer mana saja yng sudah punya content
        content request yng ada di peer di-redirect ke peer yng sudah punya content
        """
        daftar_peer_idle = []
        for k,v in self.peer_tracking.iteritems():
            if content_id in v['cache_content'] and v['status']=='IDLE':
                daftar_peer_idle.append(k)
        
        #kalau ada hasil baik banyak element atau cuma satu element:
        if daftar_peer_idle:  
            k = random.choice(daftar_peer_idle)
            return self.get_peer_from_id(k)
        else:
            return None
                    
                    
                    
 
