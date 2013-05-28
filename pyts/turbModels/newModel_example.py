from mBase import *
"""
An example module for defining a new 'turbulence/spectral model' called 'aNewModel'.

Once you have finished writing this file add it to the import line of this folder's
__init__.py script.

This turbulence model can then be specified by writing 'newModel_example.aNewModel'
on the 'TurbModel' line of the TurbSim input (config) file.

You can also create a shortcut to this model by adding:
'mymodel':newModel_example.aNewModel,
to the model_alias dictionary in the __init__.py file.  The model can then be
specified simply as 'mymodel' in the input file.

"""

class aNewModel(turbModelCohNonIEC): # Here we subclass a coherence model (defined in mBase.py).
    """
    An example class for defining a spectral model.  Each spectral model should
    subclass a coherence model class.

    This class must define an 'initModel' method that defines the '_autoSpec'
    property. '_autoSpec' is a 3 x Nz x Ny x Nf array.  This array should be
    populated with the power spectral densities for each point in the grid in
    units of m^2s^-2/hz.

    Spectral models often have a form such as:
              A
      S = ---------
           (1+B*f)^(5/3)
     where A and B are constants with units of m^2s^-2/hz and s, respectively.
    """

    def initModel(self,):
        """
        Each profile model should define this 'initModel' method to specify the
        '_u' property (i.e. the mean velocity vector-field).
        """
        # Here we define the 
        dudz=np.abs(self.profModel.dudz[:,self.grid.ihub[1]])
        dudz[dudz<0.1]=0.1
        self._autoSpec[0]=0.1*(self.profModel.uhub)**2/dudz[:,None,None]/(1.+1.8*self.f[None,None,:]/dudz)**(5./3.)
        self._autoSpec[1]=0.06*(self.profModel.uhub)**2/dudz[:,None,None]/(1.+1.8*self.f[None,None,:]/dudz)**(5./3.)
        self._autoSpec[2]=0.01*(self.profModel.uhub)**2/dudz[:,None,None]/(1.+1.8*self.f[None,None,:]/dudz)**(5./3.)
        
        # Variables that may be useful in defining profile models:
        # --- This turbModel object ---
        # self.z                 # The vertical height vector (m)
        # self.y                 # The lateral position vector (m)
        # self.ustar2            # the square of the friction velocity specified in the input file, 'UStar' (m^2/s^2)
        # self.f                 # The frequency vector (hz)
        # --- The profModel object ---
        # self.profModel._u      # the mean velocity vector-field (m/s)
        #       ...Model.u       # shortcut to ._u[0]
        #       ...Model.v       # shortcut to ._u[1]
        #       ...Model.w       # shortcut to ._u[2]
        # self.profModel._dudz   # the vertical shear of the mean velocity vector-field (1/s)
        #       ...Model.dudz    # shortcut to ._dudz[0]
        #       ...Model.dvdz    # shortcut to ._dvdz[1]
        #       ...Model.dwdz    # shortcut to ._dwdz[2]
        # self.profModel.uhub    # The hub-height u-component of velocity (m/s)
        # --- The grid object ---
        # self.grid              # The grid object.

class setCoherence(aNewModel): # Use the spectral model from the above definition.
    """
    An example class for defining a coherence model.  In this case, we subclass
    the spectral model aNewModel, and overwrite the coherence methods defined in 
    the 'turbModelCohNonIEC' class.

    To define a new coherence model, two methods can be defined: initCohere and
    calcCoh.  The former is run once at time of instantiation, the former is run
    for each combination of spatial points.  The '_work' property (array) is
    the coherence that is defined in each iteration.
    
    """


    def initCohere(self,):
        """
        This function merely initializes parameters to be used by the 'calcCoh' function.
        Because calcCoh is called multiple times, this method is provided to define
        parameters and variables once.
        """
        #                          u-prms    v-prms    w-prms
        self._coh_coefs=np.array([[3.1,0.5],[1.7,0.9],[0.9,0.93]],dtype=ts_float)


    def calcCoh(self,comp,ii,jj):
        """
        Calculate the coherence for component *comp* (0 for u,1 for v,2 for w),
        between points *ii*=(iz,iy) and *jj*=(jz,jy).

        Coherence functions are generally decaying exponentials with frequency.  They
        often have a form such as:

        coh = exp( -A * r * f / zm  )  )

        where A has units of seconds, r is the distance between points ii and jj, and
        zm is the mean-height of the two points.

        Set the values of the '_work' matrix to define the coherence at each iteration.
        The _work matrix is a Nf-element vector.
        
        """
        r=self.grid.dist(ii,jj) # The distance between points ii and jj is often useful.
        zm=(self.z[ii[0]]+self.z[jj[0]])/2
        # Here we use the [:] form to use memory efficiently.
        # Also note the use of the 'coefs' from the initCohere.
        self._work[:]=np.exp(-self._coh_coefs[comp,0]*r*self.f/(zm+self._coh_coefs[comp,1]))
        # This defines a new spectral model.


class example_ReynoldsStress(aNewModel): # Use the spectral model from the above definition.

    def initStress(self,):
        """
        By setting the variable '_rstrCoh', one can control the Reynold's Stress.

        Unlike other variables, it is a 2 x Nz X Ny array.  This is because there are only two degrees
        (e.g. u'w', u'v' or other permutations) of freedom in the Reynold's stress tensor after the
        auto-correlation components (u'u',v'v',w'w') are pre-scribed.

        _rstrCoh[0] defines the u'v' correlation component, and _rstrCoh[1] defines the u'w' component.
        See the calcStress method for how these correlations are utilized to produce a Reynold's Stress
        in the output.
        
        '_rstrCoh' has no units, it is the cross-correlation of the u'v' and u'w' components.
        
        """

        self._rstrCoh[0]=0 # No u'v' stress.
        self._rstrCoh[1]=-(1-self.z[:,None,None]/self.config['RefHt']) # The u'w' Reynold's stress decreases from a maximum value
                                                                       # of u_std*w_std at the bottom, to zero at 'RefHt'.
        self._rstrCoh[1][self.z>self.config['RefHt']]=0    # The u'w' component is zero above 'RefHt'
        # This model is essentially the same as that specified in the Tidal model.
        
