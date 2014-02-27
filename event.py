#!/usr/bin/env python

class Timeline(object):
    def __init__(self):
        self.timeline = []

    def __str__(self):
         return str(self.timeline)

    def search_event_pos(self, event_object):
        NOT_FOUND = -1
        lo, hi = 0, len(self.timeline)-1
        lo_event = self.timeline[0]
        hi_event = self.timeline[hi]
        while lo <= hi:
            #print 'CURPOS',lo,hi
            mid = int((lo + hi)/2)
            if self.timeline[mid].time < event_object.time:
                lo = mid + 1
            elif self.timeline[mid].time > event_object.time:
                hi = mid - 1
            else:
                return min(lo,hi)
                
        return min(lo,hi)

         
    def add_event(self, event_object):
        try:
            if not self.timeline:
                self.timeline.append(event_object)
                return 0
                
            idx = self.search_event_pos(event_object)
            if idx == len(self.timeline)-1:
                self.timeline.append(event_object)
            else:
                self.timeline.insert(idx+1, event_object)
                
            return idx+1
        except:
            pass
        
    def cancel_event(self, partial_e_o):
        """
        untuk menghapus suatu event, perlu:
        1. event.actor
        2. event.action
        3. event.action_param
        """
        if not self.timeline:
            return 0

        idx=0
        idx=self.search_event_pos(partial_e_o)
        self.timeline.pop(idx)
        return idx

        #idx = 0
        #for idx, ev in enumerate(self.timeline):
        #    if ev.actor == partial_e_o.actor and ev.action == partial_e_o.action:
        #        param_equal = True
        #        for p_idx, p_obj in enumerate(partial_e_o.action_params):
        #            if p_obj != ev.action_params[p_idx]:
        #                param_equal = False
        #                break
        #        if param_equal:
        #            break
        #else:
        #    return -1
        #self.timeline.pop(idx)
        #return idx
        
    def get_next_event(self):
        if self.timeline:
            return self.timeline.pop(0)
        else:
            return None
            
    def append_event(self, object_event):
        self.timeline.append(object_event)

    def __nonzero__(self):
        if self.timeline:
            return True
        else:
            return False

    def marshall(self):
        self.marshalled_timeline = [ ev.marshall() for ev in self.timeline ]
        del self.timeline

    def unmarshall(self, peer_list):
        self.timeline = []
        for m in self.marshalled_timeline:
            ev = Event(0,0)
            ev.unmarshall(m, peer_list)
            self.timeline.append(ev)

    def extend_timeline(self, other):
        if other.timeline:
            self.timeline += other.timeline

class Event(object):
    def __init__(self, type, time, actor=None, action=None, action_params=None):
        self.type = type #types 1 = request, 2 = download, 3 = save ....
        self.time = time
        self.actor = actor
        self.action = action
        self.action_params = action_params #list of parameters
        
    def execute(self):
        return self.action(*self.action_params)
        #self.action is a callable that returns a tuple of new event list and cancelled event list
        
    def __repr__(self):
        return '%s %s %s.%s'%(self.time, self.type, self.actor, self.action.__name__)
        #return [self.type, self.time, self.actor]
    
    def __str__(self):
        return '%s %s %s.%s'%(self.time, self.type, self.actor, self.action.__name__)

    def set_actor_list(self, actor_list):
        self.actor_list = actor_list

    def marshall(self):
        return {'type':self.type,'time':self.time,'actor':self.actor.id,'action':self.action.__name__,'action_params':self.action_params}

    def unmarshall(self,m, peer_list):
        self.type = m['type']        
        self.time = m['time']
        #self.actor = self.actor_list[m['actor']]
        self.actor = peer_list[m['actor']]
        self.action = getattr(self.actor, m['action'])
        self.action_params = m['action_params']
      
REQUEST = 1
DOWNLOAD = 2
UPLOAD_START = 3
UPLOAD_DONE = 4
CACHE_CONTENT = 5
REMOVE_CONTENT = 6  
UPDATE_STATE = 7
