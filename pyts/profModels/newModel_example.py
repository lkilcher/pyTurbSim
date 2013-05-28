from mBase import *
"""
An example module for defining a new 'profile model' called 'aNewModel'.

Once you have finished writing this file add it to the import line of this folder's __init__.py script.

This profile model can then be specified by writing 'newModel_example.aNewModel' on the 'WindProfileType' line of the TurbSim input (config) file.

You can also create a shortcut to this model by adding:
'mymodel':newModel_example.aNewModel,
to the model_alias dictionary in the __init__.py file.  The model can then be specified simply as 'mymodel' in the input file.

"""

class aNewModel(profModelBase):
    """
    An example class for defining the mean velocity profile.

    This class must set the values of the '_u' property (memory allocated in
    profModelBase.__init__). This is the 3 x Nz x Ny mean velocity vector-field.

    The first index of '_u' is the velocity component.  The indexes are:
      0: u-component (out of y-z plane component)
      1: v-component (lateral horizontal component)
      2: w-component (vertical component)
    
    The second index of '_u' is the z-direction, and the third is the y-direction
    of the grid.

    """

    def initModel(self,):
        """
        Each profile model should define this 'initModel' method to specify the
        '_u' property (i.e. the mean velocity vector-field).
        """
        # In this example, we set the u-component to increase linearly with height:
        self._u[0]=0.3*self.grid.z[:,None] # Arbitrarily chose a factor of 0.3
        # Note that the 'grid' object of this TurbSim run is accessible in the profile model.
        self._u[2]=self.calc_vertical_velocity()

    def calc_vertical_velocity(self):
        """
        Define as many methods as you like for helping the initModel method...
        """
        return 0.01*self.grid.y[None,:]+0.2 # Arbitrarily set the vertical velocity to increase in the y-direction (not very realistic).
