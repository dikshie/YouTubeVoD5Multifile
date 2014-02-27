#!/usr/bin/env python

import random

class CDN(object):

    def __init__(self, catalog):
        self.type = 'CDN'
        self.upload_bandwidth = 0
        self.peer_list = None
        self.content_catalog = catalog
        self.peer_tracking = dict()
        
    def set_peer_list(self, peer_list):
        self.peer_list = peer_list
        
    def get_peer_from_id(self, id):
        for p in self.peer_list:
            if p.id == id:
                return p
        else:
            return None

    def get_content(self, content_id):
        """
        reply dengan content atau redirect
        """
        this_content=self.content_catalog[content_id]
        tracked_peer = self.get_peer_tracking(content_id)
        
        
        if tracked_peer:
            #print 'tracked_peer', tracked_peer , 'content_id', content_id
            return [None, tracked_peer]
            
        #jika content tidak ada di peer (None) maka kembalikan langsung dari CDN.
        else:
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
                    
                    
                    
 
