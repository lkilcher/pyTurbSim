"""
An example module for defining a new 'profile model' called 'aNewModel'.

Once you have finished writing this file add it to the import line of
this folder's __init__.py script.

This profile model can then be specified by writing
'newModel_example.aNewModel' on the 'WindProfileType' line of the
TurbSim input (config) file.

You can also create a shortcut to this model by adding:
'mymodel':newModel_example.aNewModel, to the model_alias dictionary in
the __init__.py file.  The model can then be specified simply as
'mymodel' in the input file.

"""

from pyts.profModels.base import profModelBase


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

    def __init__(self, grid, coef_u, coef_w=[0.01, 0.2]):
        """
        Each profile model should define the __init__ method.

        The __init__ method must take the *grid* as the first input
        parameter.  All other input parameters can be specified to
        define the model.

        The *grid* input parameter is automatically added as an
        attribute of the profile model.

        This method should set all three components of the mean
        velocity field, '_u'.  The components default to 0 if they are
        not set here.
        """
        # In this example, we set the u-component to increase linearly with height:
        # Note: we are making use of the automatically added 'grid' attribute
        self._u[0] = coef_u * self.grid.z[:, None]
            # Arbitrarily chose a factor of 0.3
        # Note that the 'grid' object of this TurbSim run is accessible in the
        # profile model.
        self.coef_w = coef_w  # We can store variables for use in other methods.
        self._u[2] = self.calc_vertical_velocity()

    def calc_vertical_velocity(self):
        """
        Define as many methods as you like for helping the __init__ method...
        """
        # Note: again we make use of the automatically added 'grid' attribute, and the stored coef_w attribute.
        # Here we arbitrarily set the vertical velocity to increase in the
        # y-direction (not very realistic).
        return self.coef_w[0] * self.grid.y[None, :] + self.coef_w[1]
