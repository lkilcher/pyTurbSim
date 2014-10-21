from ..base import ts_float,np

p_coefs_unstable=[
    # u-coefs
    [0.5,105.],
    # v-coefs
    [0.95,17.],
    # w-coefs
    [0.95,2.],]
f_coefs_unstable=[
    # u-coefs
    [ts_float(2.2**(3./5.)),33],
    # v-coefs
    [2,9.5],
    # w-coefs
    [2,5.3],]

# These coefficients are copied from TSsubs.f90.
# They were calculated by Neil Kelley based on data from the NWTC.
nwtcup_coefs={'stable':{},'unstable':{}}
nwtcup_coefs['stable']['terms']={'fr_il':np.array([[0.0964,-0.316,0,-0.386,0],
                                             [0.0323,-0.388,0,-0.389,0],
                                             [0.0972,-0.0964,0,-0.616,0]],dtype=ts_float),
                           'fr_ih':np.array([[1.69,-.340,0,-.133,0],
                                             [0.473,-0.441,0,0.291,0],
                                             [0.470,-0.218,0,-0.158,0],],dtype=ts_float),
                           'Pr_il':np.array([[1.21,0.0523,0,0.189,0],
                                             [1.29,0.00664,0,0.354,0],
                                             [0.368,0.0938,0,0.109,0],],dtype=ts_float),
                           'Pr_ih':np.array([[0.224,0.170,0,0.223,0],
                                             [0.991,0.344,0,-0.605,0],
                                             [0.639,0.0354,0,-0.0319,0],],dtype=ts_float)
                           }
nwtcup_coefs['stable']['min']={'fr_il':(0.015,0.003,0.006),
                         'fr_ih':(0.35,0.25,0.2),
                         'Pr_il':(0.8,0.95,0.2),
                         'Pr_ih':(0.05,0.2,0.25),
                         }
nwtcup_coefs['stable']['max']={'fr_il':(0.4,0.23,0.175),
                         'fr_ih':(10.,3.,1.25),
                         'Pr_il':(2.25,2.25,0.75),
                         'Pr_ih':(0.8,1.0,1.0),
                         }
nwtcup_coefs['unstable']['terms']={
    'fr_il':np.array([
        [  0.08825035, -0.08806865, -0.26295052,  1.74135233, 1.86785832 ],
        [  0.58374913, -0.53220033,  1.49509302,  3.61867635, -0.98540722 ],
        [  0.81092087, -0.03483105,  0.58332966, -0.10731274, -0.16463702 ],],dtype=ts_float),
    'fr_ih':np.array([
        [  1.34307411, -0.55126969, -0.07034031,  0.40185202, -0.55083463 ],
        [  4.30596626,  0.31302745, -0.26457011, -1.41513284, 0.91503248 ],
        [  1.05515450, -0.25002535,  0.14528047,  1.00641958, -0.67569359 ],],dtype=ts_float),
    'Pr_il':np.array([
        [ 57.51578485, -1.89080610,  4.03260796,  6.09158000, -7.47414385 ],
        [ 32.06436225, -1.43676866,  3.57797045,  5.31617813, -5.76800891 ],
        [  6.60003543, -0.45005503,  1.35937877,  2.45632937, -1.98267575 ],],dtype=ts_float),
    'Pr_ih':np.array([
        [  4.52702491,  0.72447070, -0.10602646, -3.73265876, -0.49429015 ],
        [  3.93109762,  0.57974534, -0.20510478, -4.85367443, -0.61610914 ],
        [ 16.56290180,  0.40464339,  0.82276250, -3.92300971, -1.82957067 ],],dtype=ts_float),
    }
nwtcup_coefs['unstable']['min']={'fr_il':(0.2,0.12,0.2),
                           'fr_ih':(0.1,1.8,.95),
                           'Pr_il':(1.0,0.2,1.0),
                           'Pr_ih':(0.1,0.2,0.3),
                           }
nwtcup_coefs['unstable']['max']={'fr_il':(1.5,2.3,1.4),
                           'fr_ih':(8.0,7.5,1.75),
                           'Pr_il':(8.,8.,7.),
                           'Pr_ih':(1.2,0.9,1.0),
                           }

def calc_nwtcup_coefs(zL):
    p_coefs=np.empty((3,2),dtype=ts_float)
    f_coefs=np.empty((3,2),dtype=ts_float)
    if zL>0:
        dat=nwtcup_coefs['stable']
        loc_zL=fix2range(zL,0.005,3.5)
        ustar_tmp=0.
    else:
        dat=nwtcup_coefs['unstable']
        loc_zL=np.abs(fix2range(zL,-0.5,-0.025))
        ustar_tmp=fix2range(self.UStar,0.2,1.4)
    for i0,sfx in enumerate(['il','ih']):
        nm='Pr_'+sfx
        arr=dat['terms'][nm]
        p_coefs[:,i0]=fix2range(arr[:,0]*(loc_zL**arr[:,1])*ustar_tmp**arr[:,2]*np.exp(arr[:,3]*loc_zL+arr[:,4]*ustar_tmp),dat['min'][nm],dat['max'][nm])
        nm='fr_'+sfx
        arr=dat['terms'][nm]
        f_coefs[:,i0]=fix2range(arr[:,0]*(loc_zL**arr[:,1])*ustar_tmp**arr[:,2]*np.exp(arr[:,3]*loc_zL+arr[:,4]*ustar_tmp),dat['min'][nm],dat['max'][nm])
    f_coefs**=-1 # Invert the second (fr) coefficient.
    p_coefs*=f_coefs # All of the first coefficients are the product of the first and the second (inverse included).
    # The factors in unstable_coefs are included in the fits that N. Kelley did.
    p_coefs*=np.array(p_coefs_unstable,dtype=ts_float)
    f_coefs*=np.array(f_coefs_unstable,dtype=ts_float)
