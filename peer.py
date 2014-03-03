#!/usr/bin/env python

import random 
import event
import math

# class properties:  
# cache: cache entry (file_id, size, start, stop, download count), expire, request, upload

# simple peer state
#peer_state_list =['idle', 'busy']
i = 0
class Peer(object):
    
    #method __init__
    def __init__(self, id, cdn, size, up_bw, dn_bw):
        self.cache_entries=dict() #// file_id, size/len, expire
        self.size=size
        self.cdn = cdn
        self.id = id
        self.up_bw = up_bw
        self.dn_bw = dn_bw
        self.type = 'Peer'
        self.upload_bandwidth = 0
        self.content_baru = []
        #self.temporary_check=dict()
             
    def __repr__(self):
        return self.id
        
    def __str__(self):
        return str(self.id)
    
    def request_to_cdn(self, content_id, time_cur):
        """
        request ke CDN
        CDN reply dengan content atau redirect ke peer lain
        buat event untuk cache content dari CDN jika CDN reply dengan content
        buat event untuk request_to_peer jika CDN redirect ke peer lain
        """
        
                
        # cek cache entries dulu utk mencegah kasus peer yng sama me-request content id yng sama
        #
        # jika cache_entries[content_id] sudah ada return []
        if self.cache_entries.has_key(content_id):
            return [],[]
        
        other_reply = self.cdn.get_content(content_id, time_cur)
        if other_reply[0]:
            content = other_reply[0]
       
                        
            #pada prinsipnya cache_event ini adalah mendownload kemudian menyimpan 
            #cache_content event, download duration, actor, actor action, action parameters
            # tandai bahwa cache entry akan di-isi content sebenarnya
            self.cache_entries[content_id] = 1

            #contoh: {1: [1, 34.433471105806156, 258.0, 3600.0] }
            durasi = content[2]*8/(self.up_bw/1000.0)
            cache_event = event.Event(event.CACHE_CONTENT, time_cur+durasi, self, self.cache_content, [content_id, content, time_cur+durasi])

            return [cache_event],[]
            
        else:
            request_to_peer_event = event.Event(event.REQUEST, time_cur, self, self.request_to_peer, [content_id, other_reply[1], time_cur])
            return [request_to_peer_event],[]
            
        
    def request_to_peer(self, content_id, other, time_cur):
        """
        request ke peer lain (other)
        """
        #ambil content ke peer, hasilnya content 
        content = other.get_content(content_id,time_cur) 
        
        #ekstrak nilai panjang file
        #print content
        #contoh: {1: [1, 34.433471105806156, 258.0, 3600.0] }
        durasi = (content[2]*8)/(self.up_bw/1000.0)
        
        #event utk upload done
        upload_done_event = event.Event(event.UPLOAD_DONE, time_cur+durasi, other, other.upload_done, [other.id, content_id, 'BUSY'])
        
        new_remove_content_event, old_remove_content_event = other.change_content_expiry_time(content, time_cur)
              
        
        # tandai bahwa cache entry akan di-isi content sebenarnya
        self.cache_entries[content_id] = 1
        
        # bikin cache_content event
        cache_event = event.Event(event.CACHE_CONTENT, time_cur+durasi, self, self.cache_content, [content_id, content, time_cur+durasi])
        
        #kembalikan event
        return [cache_event, upload_done_event, new_remove_content_event] , [old_remove_content_event]
        
        
        
    def upload_done(self, peer_id, content_id, type):
        """
        Method utk report upload done
        """
        self.cdn.receive_report_from_peer(peer_id, content_id, 'IDLE')
        return [],[]
        
        
            
    def get_content(self, content_id, time_cur):
        """
        ambil content dari peer
        """
        
        #upload ke peer lalu lapor state jadi UPLOADING
        self.cdn.receive_report_from_peer(self.id, content_id, 'UPLOADING')
        
        return self.cache_entries[content_id]
        
            

    def cache_content(self, content_id, content, time_cur):
        """
        cache the content in the peer
        and report to CDN
        karena membutuhkan cdn class dng method report_to_cdn
        """
        
        #algoritma TTC

        #n_ir = total number of the times that video i has been requested
        #t_ir = the last time video i was requested
        n_ir = self.cdn.get_number_requested_video(content_id)
        t_ir = self.cdn.get_video_last_time_requested(content_id)
        #a_i = waktu content saat content di upload
        #contoh: {0: [0, 5.0775931306168065, 499.0, 3600.0]}
        a_i = content[1]
        #print content_id, a_i, n_ir, t_ir
        kanan = abs((1.0)/(time_cur - t_ir))
        kiri = abs((n_ir)/(t_ir - a_i))
        #print 'kiri ', kiri , 'kanan', kanan

        #hitung P_i:
        P_i = min(kiri,kanan)
        #if P_i == 0:
        #    P_i = 0.0001

        #hitung P_i_min
        P_i_min =  0.00001

        #print P_i, P_i_min

        #hitung TTC
        TTC = abs((math.log(P_i) - math.log(P_i_min))/P_i)
        #print 'TTC ', TTC, P_i, P_i_min

        #extract time to expiry menjadi expiry time
        #ada di content[2]+time_cur
        
    
        self.content_baru=[content[0], content[1], time_cur+TTC ]
        self.cache_entries[content_id]=self.content_baru
        
        #self.time_cur = time_cur
        
        self.cdn.receive_report_from_peer(self.id, content_id, 'CACHE')
        
        
        #utk expiry time gunakan content_baru[2] di atas.
        expire_event=event.Event(event.REMOVE_CONTENT, self.content_baru[2], self, self.remove_content, [content_id])
        return [expire_event],[]
    
    
    def remove_content(self, content_id):
        """
        menghapus cache
        """
        #print self.id, content_id
        self.cdn.receive_report_from_peer(self.id, content_id, 'REMOVE_CACHE')
        
        del self.cache_entries[content_id]
        return [],[]
    
    def change_content_expiry_time(self, content, time_cur):
        """
        mengubah content expiry time, misalnya saat upload content yang akan expire waktu content sedang diupload
        """
        #contoh: {1: [1, 34.433471105806156, 258.0, 3600.0] }
        #ambil informasi expiry time content
        content_id = content[0]
        
        #load time_expiry dari self.cache_entries 
        time_lama = self.cache_entries[content_id][2]

        #hitung durasi dan time_baru
        #contoh: {1: [1, 34.433471105806156, 258.0, 3600.0] }
        durasi = (content[2]*8)/(self.up_bw/1000.0)
        time_baru = time_cur + durasi

        if time_baru > time_lama:  #durasi download > cachetime
            new_expire_event = event.Event(event.REMOVE_CONTENT, time_baru, self, self.remove_content, [content[0]])
            old_expire_event = event.Event(event.REMOVE_CONTENT, time_lama, self, self.remove_content, [content[0]])
            return [new_expire_event, old_expire_event]
        else:
            return None, None
        
