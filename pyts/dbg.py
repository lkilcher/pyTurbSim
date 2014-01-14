import numpy as np
import time

class timer(object):
    def __init__(self,label='NONE'):
        self.tnew=0.
        self.total=0.
        self.label=label

    def start(self,):
        self.tnew=time.time()

    def reset(self,):
        self.total=0.
        self.start()

    def stop(self,):
        self.total+=time.time()-self.tnew

    def __repr__(self):
        return "So far the *%s* timer has clocked %0.3f seconds." % (self.label,self.total)


def vec2full(arr):
    shp=arr.shape
    n=int((np.sqrt(8*shp[0]+1)-1)/2)
    oshp=[n,n]+list(shp[1:])
    g=np.zeros(oshp,dtype=arr.dtype)
    indx=0
    for jj in range(n):
        for ii in range(jj,n):
            if ii==jj:
                g[ii,jj]=arr[indx]
            else:
                g[ii,jj]=arr[indx]
                g[jj,ii]=arr[indx]
            indx+=1
    return g
