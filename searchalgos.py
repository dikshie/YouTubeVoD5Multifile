#!/usr/bin/env python
import time



def search_event_pos(li, key):
        lo,hi = 0, len(li)

        #mempersempit search space (bagi dua)
        #lo, hi = 0, len(self.timeline)//2
        counters=0
        while lo < hi:
            mid = (lo+hi)//2
            if li[mid] < key:
                lo = mid + 1
            else:
                hi = mid
            counters+=1
        print 'BISECT COUNTERS 2 :', counters, len(li), lo
        return lo


dual_count = 0

def dual_pivot(li,key, lo=0, hi=0):
    global dual_count

    if lo==hi or lo == hi - 1:
        return lo

    p = lo + (hi-lo)//3
    q = lo + 2 * (hi-lo)//3

    dual_count += 1

    if key < li[p]:
        return dual_pivot(li,key,lo,p)

    elif (key > li[p] and key < li[q]):
        return dual_pivot(li,key,p+1,q)

    elif key > li[q]:
        return dual_pivot(li,key,q+1,hi)
    
    if key == li[p]:
        #print 'DUAL PIVOT', dual_count, p
        return p
    else:
        #print 'DUAL PIVOT', dual_count, q
        return q


if __name__ == "__main__":
    dual_count = 0
    li = [0,1,2,3,4,5,6,9,10];
    left = 0
    right = len(li)
    for key in [8,6,1,12,7]:
        dual_count = 0
        #index = search_event_pos(li, key)
        index = dual_pivot(li, key, 0, len(li))
        print key, index