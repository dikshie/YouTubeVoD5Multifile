#!/usr/bin/env python

import time
import random
import math
from scipy.stats import expon
from scipy.stats import beta 
import cPickle as pickle
from multiprocessing import Pool

start = 0 #mulai waktu dari 0
end1= (30*24*3600) #1 bulan
#end2= (36*7*24*1*3600) #36 minggu
jam =  30*24

#format =  {'video_id': video_id, 'uploaded': uploaded , 'viewcountterminus': viewcountterminus, 'alpha': alpha_ , 'beta': beta_}
catalog = {}

i=0
expected=100 #expected 100 videos/hour
multiple_of=range(200000)

#video catalog generator utk parameter alpha,beta,timeuplaoded sudah OK.
while i < jam :     
    #video diupload mengikuti poisson process
    #rate 100 videos/hour
    #bikin event utk 500 videos (5jam)
    #we dont care about time.  
    #we only care about poisson process for these video's uploaded time.
    tx=random.expovariate(expected)
    start = start + (tx*expected)
    video_id = i
    
    #untuk tiap video-id dapatkan peak time (minggu peak time)    
    #random exponential sampling peak time  (dari graph cdf time to peak in weeks(x) )
    #dapatkan minggu ke-n saat peak.utk kemudian menentukan alpha dan beta

    R= expon.rvs(size=100) #jumlah sampling
    R= R*10 # interval diperbesar 10 kali.
    panjang=len(R)
    j=0
    pilih=[]
    while j<panjang:
        pilih.append(math.floor(R[j]))
        j=j+1
    hasil=random.choice(pilih)
    if hasil in range(1,36):
        hasil=hasil  #dalam resolusi 1 minggu
    else:
        hasil=1.0    #dalam resolusi 1 minggu
    
    #random sampling dari count view terminus
    #dapatkan maximum count view
    terminus = random.randint(4,1069464)  #dalam resolusi 1 minggu
    
    #estimasi beta function:
    pilihan_alpha=[1,2]
    alpha_ = random.choice(pilihan_alpha) #fixed alpha
    mode = (hasil/36.0) #peak time di-scaling ke interval 0<time_peak<1
    beta_ = ((alpha_-1 ) - (mode*alpha_) + (2*mode))/mode
    #print i, hasil, alpha_ , beta_
    
    #masukkan ukuran video secara random
    #satuan MB
    size = random.randint(1,200)
    
    #catalog video
    #video id , waktu diupload, view count terminus, alpha_, beta_
    #masukkan ke catalog:
    
    if not catalog.has_key(video_id):
        catalog[video_id]={'video_id':video_id, 'uploaded':start, 'size':size, 'viewcounterminus':terminus, 'alpha':alpha_ , 'beta':beta_, 'pdf':{}, 'cdf':{} }

    i+=1
    
print catalog
print len(catalog)

"""
#ini bagian menambahkan pdf dan cdf utk tiap selang.

j=0 #asumsi iterator waktu dalam satuan detik.
skala = 36*7*24*3600 #36 minggu dalam satuan detik.

#ambil waktuuploaded terakhir video id terakhir tuk ditambahkan ke akhir
numbervideo=len(catalog)
video_id_terakhir = len(catalog) - 1

temp=catalog[video_id_terakhir]['uploaded'] #dalam detik
akhir=skala+temp #dalam detik

while j < akhir:
    #simulasi dalam detik
    #utk tiap video:
    
    if j >= multiple_of[0]*7200:
        for k in range(numbervideo):
            alpha_a=catalog[k]['alpha']
            beta_a=catalog[k]['beta']
            #hitung pdf dan cdf
            cdf_a = beta.cdf(j,alpha_a,beta_a,loc=0,scale=skala)
            pdf_a = beta.pdf(j,alpha_a,beta_a,loc=0,scale=skala)
            catalog[k]['cdf'][j]=cdf_a
            catalog[k]['pdf'][j]=pdf_a
        multiple_of.pop(0)
        print j
    j+=1    

with open('catalog.pickle', 'wb') as handle:
    pickle.dump(catalog, handle)
handle.close()    
"""