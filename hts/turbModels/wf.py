from nwtc import *
    
class inf_turb(NWTCgenModel):
    _coefs={'stable':{},'unstable':{}}
    _coefs['stable']=np.rollaxis(np.array([
        [# Low Freq !MUST BE FIRST.
            [#P coefs
                [ 0.88418, 11.665367, 0.794753, 1.55288, 1.56925,   1.50 ],#u
                [ 0.4671733, 4.3093084, 0.859202, 0.90382, 1.59076, 0.75 ],#v
                [ 0.076136, 2.644456, 1.207014, 0.533202, 1.51415,  1.0  ]],#w
            [#f coefs
                [ 0.009709, 0.4266236, 1.644925, 0.045, 0.212038, 2.00  ],
                [ 0.0220509, 0.93256713, 1.719292, 0.160, 0.74985, 1.15 ],
                [ 0.0351474, 1.4410838, 1.833043, 0.350, 1.645667, 1.0  ]]],
        [ # High Freq
            [#P coefs
                [ 0.8029768, 1.708247, 3.669245, 1.5431, 1.6379, 0.01   ],
                [ 0.419234 , 2.759119, 1.4483715, 0.89717, 1.67034, 1.30],
                [ 0.239692 , 2.3531204, 1.062937, 0.5324, 1.6314, 1.5   ]],
            [#f coefs
                [ 0.042393, 1.28175, 1.409066, 0.045, 0.21137, 3.5      ],
                [ 0.220831, 0.630632, 0.8120686, 0.160, 0.74876, 1.25   ],
                [ 0.382558, 1.3640485, 1.524565, 0.350, 1.638806, 1.5   ]]],
        ]),2) # The dims of this (after the rollaxis) are (uvw,low/high,P/f,...)
    
    def calcCoefs(self,):
        x=self._loc_zL
        if self.stable:
            dat=self._coefs['stable']
            num=dat[...,0]+(dat[...,1]*x)**dat[...,2]
            den=np.empty_like(num)
            den[:,:,0,:]=dat[...,0,3]*np.exp(dat[...,0,4]*x)
            den[:,:,1,:]=dat[...,1,3]+dat[...,1,4]*x
            out=num/den
            # An exception for the w-comp. low-freq, P-val:
            out[2,0,0]-=1.75*x
            # An exception for the w-comp. high-freq, P-val:
            out[2,1,0]-=2.*x
            if out[2,1,0]<0:
                out[2,1,0]=1.0
            # An exception for the u-comp. low-freq, f-val:
            out[0,0,1]=np.abs(out[0,0,1]-3.*x)
            out*=dat[...,5]
        else:
            dat=self._coefs['unstable']
            out=np.empty((self.n_comp,2,2),dtype=ts_float)

            zi_uvlimit=1350
            zi_wlimit=1600
            # What an unbelievable mess!!!
            # The functions are all different, so using _coefs is too much of a pain!
            #### Low Frequency
            # p-coefs
            out[0,0,0] = 2.00 * ( -0.436922  + 2.784789 / ( 1.0 + np.exp( -(x - 0.104094) / 0.136708 ) ) ) / (  0.1392684 + 1.7396251*x )
            out[1,0,0] = 0.25 * ( 0.467006  + (5.3032075*x)**1.1713260) / ( 0.1425146 + 2.2011562*x )
            out[2,0,0] = ( 0.086908   + (2.3719755 *x)**1.3106297) / ( 0.00251981 + (0.50642167*x)**0.6607754 )
            # f-coefs
            out[0,0,1] = ( 0.467962 + 0.9270681*np.exp( -x / 0.02039003 )) / ( 0.759259 - 0.1448362*x )
            out[1,0,1] = 2.25 * (( 0.369625 + 1.0772852*np.exp( -x / 0.0210098 ))) / ( 0.759259 - 0.1448362*x )
            out[2,0,1] = 2.25 * ( 3.39482 * np.exp( 0.279914*x )) / ( 4.59769 + 12.58881*np.exp( -x / 0.03351852 ) )
            #### High Frequency
            #P-coefs
            out[0,1,0] = 0.10 * ( 0.691114  + 0.0791666*x    ) / ( 0.77991   + 0.1761624  / ( 1.0 + np.exp( -(x - 0.0405364) / (-0.0184402) ) )  )
            out[1,1,0] = ( 0.421958 * np.exp( 0.20739895*x )) / ( 0.5247865 + 0.0419204 / ( 1.0 + np.exp( -(x - 0.0434172) / (-0.0179269) ) ) )
            out[2,1,0] = 0.80 * ( 0.222875  + 0.1347188*x) / ( 0.3542331 + 0.0168806 / ( 1.0 + np.exp( -(x - 0.0388899) / (-0.0220998) ) ) )
            #f-coefs
            out[0,1,1] = 1.75 * ( 0.047465  + 0.0132692*x) / ( 0.0599494 - 0.0139033*np.exp(-x / 0.02603846) )
            out[1,1,1] = 1.50 * ( 0.18377384 * np.exp( 0.2995136*x )) / ( 0.1581509  + 0.09501906*x )
            out[2,1,1] = 2.0 * ( 0.3419874 + 0.24985029 * np.exp(-x / 0.02619489)) / ( 0.451295  + 0.2355227*x )
            if self.ZI > zi_uvlimit:
                out[0,0,1]*= self.ZI / zi_uvlimit
                out[0,1,0]*=self.ZI / zi_uvlimit
                out[1,1,1]*= self.ZI / zi_uvlimit
                out[1,0,1]*=self.ZI / zi_uvlimit
            if self.ZI > zi_wlimit:
                out[2,0,1]*=4.0*self.ZI / zi_wlimit
                out[2,1,1]*= 0.35*self.ZI / zi_wlimit
        out[:,:,1]**=-1 # Invert the second (fr) coefficient.
        out[:,:,0]*=out[:,:,1] # All of the first coefficients are the product of the first and the second (inverse included).
        return out
        
    def initModel(self,):
        if self.stable:
            self._loc_zL=min(self.zL,0.15)
        else:
            self._loc_zL=max(self.zL,-1.)
        self.coefs=self.calcCoefs()


    ## def _beta4(self,x,a):
    ##     return a[0]*np.exp(-x/a[1])+a[2]*np.exp(-x/a[3])
    ## def _beta5(self,x,a):
    ##     return a[0]/(1.0+np.exp((a[1]-x)/a[2]))

class outf_turb(NWTCgenModel):

    def _beta1(self,x,a):
        tmp1=x-a[1]
        tmp2=a[2]/2.
        return a[0]/(1.0+np.exp(-(tmp1+tmp2)/a[3]))*(1.0-(1.0+np.exp(-(tmp1-tmp2)/a[3])))

    def _beta2(self,x,a):
        return a[0]/(2.50663*a[2])*np.exp(-0.5*((x-a[1])/a[2])**2)

    def _beta3(self,x,a):
        return 0.5*a[0]*(1.0+self._beta10( (x-a[1])/(1.414*a[2])))

    def calcCoefs(self,):
        x=self._loc_zL
        if self.stable:
            out=np.empty((self.n_comp,2,2),dtype=ts_float)
            ### Low Freq.
            #P-vals
            out[0,0,0] = 0.9 * ( 0.894383 + (1.55915 * x)**3.111778)/( 1.563317 * np.exp(1.137965 * x))
            out[1,0,0] = 0.60 * (( 0.747514 + (1.57011 * x)**1.681581)/( 0.910783 * np.exp(1.1523931 * x)) - 1.75 * x)
            out[2,0,0] = 0.6 * (( 0.376008 * np.exp(1.4807733* x))/( 0.539112 * np.exp(1.124104 * x)) - 2.0 * x)
            #f-vals
            out[0,0,1] = max(1.5 * (( 0.023450 + (0.3088194 * x)**1.24710)/( 0.045    +  0.209305  * x) - x),0.1)
            out[1,0,1] = 0.5 * ( 0.051616 + (0.8950263 * x)**1.37514)/( 0.160    +  0.749661  * x)
            out[2,0,1] =( 0.250375 - 0.690491  * x + 2.4329342 * x**2)/( 0.350    + 1.6431833 * x)
            ### High Freq.
            #P-vals
            out[0,1,0] = 0.35 * ( 0.149471 + 0.028528 * np.exp( -np.exp( -( (x - 0.003580) / 0.0018863 ) ) - ( (x - 0.0035802) / 0.0018863) + 1.0))/( 1.563166  * np.exp(1.137965 * x))
            out[1,1,0] = 2.25 * ((self._beta3(x, [ 2.66666062, 0.0034082, 0.0229827,])+beta1(x,[ 33.942268,  0.0160732, -0.008654,  0.0053586]))*0.9170783 * np.exp(1.152393 * x))**-1
            out[2,1,0] = 0.9  * (self._beta3(x, [ 0.1990569, 0.0286048, 0.006751,]) + self._beta2(x,[ 0.0435354, 0.0599214, 0.0520877,]))/(0.539112  * np.exp(1.124104 * x))
            #f-vals
            tmp    = -(x - 0.037003738) / 0.01612278
            out[0,1,1] = (0.764910145 + 0.654370025 * np.exp( -np.exp(tmp) + tmp + 1.0 ))/(0.045 + 0.209305  * x)
            out[1,1,1] = 0.5 * (self._beta3(x, [ 0.5491507, 0.0099211, 0.0044011,]) + self._beta2(x, [ 0.0244484, 0.0139515, 0.0109543,]))/(0.160 + 0.7496606 * x)
            out[2,1,1] = 2.0 * ( 0.391962642 + 0.546722344*np.exp( -0.5* ( (x - 0.023188588) / 0.018447575)**2 ))/( 0.350 + 1.6431833 * x)
        else:
            out=np.NaN*np.empty((self.n_comp,3,2),dtype=ts_float) # An extra term for the wake. u,w will be NaN
            ### Low Freq.
            # P-vals
            out[0,0,0] = 4.0 * ( ( 0.796264 + 0.316895 / (1.0 + np.exp( -(x - 0.082483) / 0.027480 )) ) / ( 0.07616  + np.exp(0.303919 * x * 0.390906) ) )
            if self.ZI < 1600.0:
                out[0,0,0]*= self.ZI / 1600.0
            out[0,0,0]=np.abs(out[0,0,0])
            out[1,0,0] =  ( 0.812483 + 0.1332134 * x ) / ( 0.104132 + np.exp(0.714674 * x * 0.495370) ) *self.ZI/1600
            out[2,0,0] = 0.75 * ( ( 0.371298  + 0.0425447 * x ) / ( 0.0004375 + np.exp(0.4145751 * x * 0.6091557) ) )
            # f-vals
            out[0,0,1] = 1.5 * ( ( 0.859809 * np.exp(0.157999 * x) ) / ( 0.81459 + 0.021942 * x) )
            if (self.ZI > 1850.0):
                out[0,0,1]*=2.6 * self.ZI / 1850.0
            out[1,0,1] = 3.0 * ( ( 0.8121775 * np.exp( -x / 4.122E+15 ) - 0.594909 * np.exp( -x / 0.0559581 ) ) / ( 0.72535  - 0.0256291 * x) )*self.ZI/1600
            out[2,0,1] = 0.9 * ( ( 6.05669  * np.exp(-0.97418 * x) ) / ( 3.418386 + 9.58012 / (1.0 + np.exp( -(x - 0.0480283) / (-0.022657) ))) )
            ### High Freq.
            # P-vals
            out[0,1,0] = 0.1 * ( ( 0.598894  + 0.282106  * np.exp(-x / 0.0594047) ) / ( 0.600977  + 9.137681  / (1.0 + np.exp( -(x + 0.830756) / (-0.252026) ))) )
            out[1,1,0] = 5.0 * ( ( 0.4830249 + 0.3703596 * np.exp(-x / 0.0553952) ) / ( 0.464604  + 1.900294  / (1.0 + np.exp( -(x + 0.928719) / (-0.317242) ))) )
            out[2,1,0] = 1.25 * ( ( 0.320112  + 0.229540  * np.exp(-x / 0.0126555) ) / ( 0.331887  + 1.933535  / (1.0 + np.exp( -(x + 1.19018 ) / (-0.3011064) ))) )
            # f-vals
            out[0,1,1] =  0.3 * (  ( 0.049279 + np.exp(0.245214 * x * 2.478923) ) / (-2.333556 + 2.4111804 / (1.0 + np.exp( -(x + 0.623439) / 0.1438076))) )
            out[1,1,1] =  2.0 * (  (-2.94362   + 3.155970 / (1.0 + np.exp( -(x + 0.872698) / 0.245246)) ) / ( 0.0171463 + 0.188081 / (1.0 + np.exp( -(x + 0.711851) / 0.688910))) )
            out[2,1,1] = 1.75 * ( ( 0.7697576 * np.exp( -x / 3.8408779 ) - 0.561527 * np.exp( -x / 0.1684403 ) ) / ( 0.512356  - 0.044946  / (1.0 + np.exp( -(x - 0.066061) / (-0.0121168) ))) )
            if self.ZI < 1350.0 :
                out[2,1,1]*= ZI / 1350.0
            ### Wake term, v-component only
            # P-vals
            out[1,2,0] = 0.05 * ( ( 0.247754 + 0.16703142 * np.exp(-x / 0.1172513) ) / ( 0.464604 + 1.900294 / (1.0 + np.exp( -(x + 0.928719) / (-0.317242) ))) )
            # f-vals
            out[1,2,1] = 3.0 * ( ( 0.72435 / (1.0 + np.exp( -(x - 0.0436448) / 0.08527 ))  ) / ( 0.0171463 + 0.188081 / (1.0 + np.exp( -(x + 0.711851) / 0.688910))) )
        out[:,:,1]**=-1 # Invert the second (fr) coefficient.
        out[:,:,0]*=out[:,:,1] # All of the first coefficients are the product of the first and the second (inverse included).
        return out
            
    def initModel(self,):
        self._loc_zL=np.abs(fix2range(self.zL,-1.0,0.4))
        self.coefs=self.calcCoefs()
            
class gp_llj(NWTCgenModel):

    @property
    def _loc_zL(self,):
        if not hasattr(self,'_val_loc_zL'):
            zlims=[50,140]
            z=self.grid.z
            out=np.empty_like(z)
            ilow=z<zlims[0]
            ihgh=z>zlims[1]
            out[ilow]=z[ilow]/self.L
            out[ihgh]=self.zL
            #if !!!CHECKTHIS... I'm not done here.
        return self._val_loc_zL

    def initModel(self,):
        self._loc_ustar=fix2range(self.config['UStar'],.15,1.0)
        self._loc_zL2=fix2range(self._loc_zL,-1.,1.)
        self.coefs=self.calcCoefs()
        print self.coefs

    def calcCoefs(self,):
        # !!!VERSION_INCONSISTENCY: there is some funny business here about
        # z/L and u* profiles, as opposed to 'mean' values (see doc).  I don't understand
        # how this is implemented, so I will proceed the same as in the above
        # models for now...
        out=np.ones((3,2,2),dtype=ts_float)
        if self.stable:
            zl_loc=max(self._loc_zL,0.025) # Can't combine this with the fix2range above
                                      # because phiM and phiE depend on self.zL
            ustar_loc=self.ustar
            ### Low Freq.
            # P-val
            out[0,0,0] =  0.003043*(  zl_loc**(-0.60526081))*(ustar_loc**(-2.4348077) )*np.exp( 1.386013230*zl_loc+2.185372290*ustar_loc)
            out[1,0,0] =  0.0222952*( zl_loc**( 0.18448738))*(ustar_loc**(-2.23473414))*np.exp(-1.216594402*zl_loc+1.491864128*ustar_loc)
            out[2,0,0] =  0.
            # f-val
            out[0,0,1] =  0.014746*(  zl_loc**(-0.37495232))*(ustar_loc**(-0.6167086) )*np.exp(-0.994591040*zl_loc+1.676298830*ustar_loc)
            out[1,0,1] =  0.0008437*( zl_loc**(-0.79592929))*(ustar_loc**(-1.78297586))*np.exp( 1.316511335*zl_loc+0.175154746*ustar_loc)
            out[2,0,1] =  1.
            ### High Freq.
            # P-val
            out[0,1,0] = 15.468066*(  zl_loc**( 0.27375765))*(ustar_loc**( 1.8091998) )*np.exp(-0.266223760*zl_loc-3.091731900*ustar_loc)
            out[1,1,0] =  1.6568440*( zl_loc**(-0.03919916))*(ustar_loc**( 0.57537263))*np.exp(+0.282805584*zl_loc-1.199845489*ustar_loc)
            out[2,1,0] =  0.69547455*(zl_loc**(-0.00800265))*(ustar_loc**(-0.1352012) )*np.exp( 0.041784840*zl_loc-0.003785870*ustar_loc)
            # f-val
            out[0,1,1] =  0.043108*(  zl_loc**(-0.39311528))*(ustar_loc**(-2.1719048) )*np.exp( 0.152732100*zl_loc+2.939119120*ustar_loc)
            out[1,1,1] =  1.5278523*( zl_loc**(-0.14197939))*(ustar_loc**( 0.02684469))*np.exp(-0.261902952*zl_loc-0.672772974*ustar_loc)
            out[2,1,1] =  0.97627403*(zl_loc**(-0.05470045))*(ustar_loc**(0.09666427) )*np.exp(-0.301255210*zl_loc-0.063122900*ustar_loc)
        else:
            pass # The unstable coefficients are simply ones.
        return out
        
