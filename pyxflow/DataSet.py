"""File to interface with XFlow xf_DataSet objects in various forms"""

# Versions:
#  2013-09-25 @dalle   : First version

# ------- Modules required -------
# Used for more efficient data storage
import numpy as np
# The background pyxflow workhorse module
import pyxflow._pyxflow as px
# Matplotlib for plotting
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation

# ------- Class for xf_Geom objects -------
class xf_DataSet:
    """A Python class for XFlow xf_DataSet objects"""
    
    # Initialization methd
    def __init__(self, ptr=None, fname=None, Mesh=None):
        """
        DataSet = xf_DataSet(ptr=None, fname=None, Mesh=None)
        
        INPUTS:
           ptr     : integer pointer to existing C xf_DataSet struct
           fname   : file name for a '.data' file to read the xf_DataSet from
           Mesh    : pointer to xf_Mesh, required if reading from file
        
        OUTPUTS:
           DataSet : an instance of the xf_DataSet Python class
        
        This function initializes a DataSet object in one of three ways.  The
        main method is to use a pointer that was previously created.  If the
        `ptr` key is not `None`, the function assumes the DataSet already exists
        on the heap and will read from it.  If `ptr` is `None` and both `fname`
        and `Mesh` are not `None`, the function will attempt to read the DataSet
        from file.  Finally, in all other cases, an empty DataSet is allocated.
        """
        # Versions:
        #  2013-09-25 @dalle   : First version
        
        # Set the defaults.
        self.nData = 0
        
        # Check the parameters.
        if ptr is not None:
            # Set the pointer.
            self._ptr = ptr
            self.owner = False
        elif fname is not None and Mesh is not None:
            # Read the file and get the pointer.
            ptr = px.ReadDataSetFile(Mesh, fname)
            # Set it.
            self._ptr = ptr
            self.owner = True
        else:
            # Create an empty geom.
            ptr = px.CreateDataSet()
            # Set the pointer
            self._ptr = ptr
            self.owner = True
            # Exit the function
            return None
            
        # Get the number of components.
        nData = px.nDataSetData(self._ptr)
        # Get the components
        self.Data = [xf_Data(self._ptr, i) for i in range(self.nData)]
    
    
    # xf_DataSet destructor method
    def __del__(self):
        """
        xf_DataSet destructor
        
        This function reminds the pyxflow module to clean up the C
        xf_DataSet object when the Python object is deleted.
        """
        # Version:
        #  2013-09-25 @dalle   : First version
        
        if self.owner and self._ptr is not None:
            px.DestroyDataSet(self._ptr)


# ---- Class for xf_Data struts ----
class xf_Data:
    """A Python class for XFlow xf_Data objects"""
    
    # Initialization method
    def __init__(self, DataSet, i=None):
        """
        Data = xf_Data(DataSet, i=None)
        
        INPUTS:
           DataSet : pointer to xf_DataSet struct
           i       : index of xf_Data to use
        
        OUTPUTS:
           Data    : an instance of the xf_Data class
               .Title : title of the xf_Data object
               .Type  : xf_Data type, see xfe_DataName
               .Data  : instance of xf_[Vector,VectorGroup] class
               ._Data : pointer to corresponding DataSet->Data
        """
        # Versions:
        #  2013-09-26 @dalle   : First version
        
        # Set the initial fields.
        self.Title = None
        self.Type  = None
        self.Data  = None
        self._ptr  = None
        # Check for bad inputs.
        if DataSet is None:
            return None
        
        # Read from data if appropriate
        if i is not None:
            # Fields
            self.Title, self.Type, self._ptr, _Data = px.GetData(DataSet, i)
        
        # Do a switch on the type
        if self.Type == 'VectorGroup':
            # Assign the vector group
            self.Data = xf_VectorGroup(_Data)


# ---- Class for xf_VectorGroup ----
class xf_VectorGroup:
    """A Python class for XFlow xf_VectorGroup objects"""
    
    # Initialization method
    def __init__(self, ptr):
        """
        VG = xf_VectorGroup(ptr)
        
        INPTUS:
           ptr : pointer to xf_VectorGroup (DataSet->D->Data)
           
        OUTPUTS:
           VG  : instance of xf_VectorGroup object
           
        This function creates a VectorGroup object from a pointer.
        """
        # Versions:
        #  2013-09-26 @dalle   : First version
        
        # Check the pointer.
        if ptr is None:
            raise NameError 
        # Set the pointer.
        self._ptr = ptr
        # Get the pointers to the vectors.
        self.nVector, V = px.GetVectorGroup(ptr)
        # Get the vectors.
        #self.V = V
        self.Vector = [xf_Vector(Vi) for Vi in V]

    def GetVector(self, role="ElemState"):
        _ptr = px.GetVectorFromGroup(self._ptr, role)
        return xf_Vector(_ptr)
     
# ---- Class for xf_Vector ----
class xf_Vector:
    """A Python class for XFlow xf_Vector objects"""
    
    # Initialization method
    def __init__(self, ptr):
        """
        V = xf_Vector(ptr)
        
        INPUTS:
           ptr : ponter to xf_Vector
        
        OUTPUTS:
           V   : instance of xf_Vector class
           
        This function creates an xf_Vector object from pointer.
        """
        # Versions:
        #  2013-09-26 @dalle   : First version
        
        # Check the pointer.
        if ptr is None:
            raise NameError
        # Set the pointer.
        self._ptr = ptr
        # Get the information and pointers to GenArrays.
        (self.nArray, self.Order, self.Basis, 
             self.StateName, GA) = px.GetVector(ptr)
        # Get the GenArrays
        self.GenArray = GA
        self.GenArray = [xf_GenArray(G) for G in GA]

    def Plot(self, Mesh, EqnSet, **kwargs):
        dim = Mesh.Dim

        if kwargs.get('xmin') is not None:
            xmin = kwargs['xmin']
        else:
            xmin = [None for i in range(dim)]

        if kwargs.get('xmax') is not None:
            xmax = kwargs['xmax']
        else:
            xmax = [None for i in range(dim)]

        for i in range(dim):
            if xmin[i] is None: xmin[i] = self.Coord[:,i].min()
            if xmax[i] is None: xmax[i] = self.Coord[:,i].max()

        if kwargs.get('figure') is not None:
            self.figure = kwargs['figure']
        else:
            self.figure = plt.figure()

        if kwargs.get('axes') is not None:
            self.axes = kwargs['axes']
        else:
            self.axes = self.figure.gca()

        Name = kwargs.get('scalar')

        x, y, tri, scalar = px.ScalarPlotData(self._ptr, Mesh._ptr, EqnSet._ptr, Name, xmin, xmax)

        if dim > 1:
            T = Triangulation(x, y, triangles=tri)
            self.axes.tripcolor(T, scalar, shading='gouraud')
        else:
            self.axes.plot(x, scalar)

        if kwargs.get('reset_limits', True):
            self.axes.set_xlim(xmin[0], xmax[0])
            self.axes.set_ylim(xmin[1], xmax[1])

        self.figure.savefig("figure.pdf")
        
#    # Scalar calculation function
#    def get_scalar(self, u, scalar=None):
#        """
#        M = V.get_scalar(u, scalar=None)
#        
#        INPUTS:
#           u      : array of state values
#           scalar : name of scalar to calculate (Note 1)
#        
#        OUTPUTS:
#           M      : array of scalar values
#        
#        This function calculates a scalar based on the available states.  The
#        dimensions of `u` must match the 'StateRank' for the input Vector `V`.
#        
#        NOTES:
#           (1) Additional scalar names available for Navier-Stokes equation sets
#               include 'Mach', 'Pressure', and 'Entropy'.
#        
#        """
#        # Versions:
#        #  2013-10-06 @dalle   : First version
#        
#        # Check if the state is available.
#        if scalar in self.StateName:
#            # Extract the state directly.
#            M = u[:,self.StateName.index(scalar)]
#        elif scalar is None:
#            # Default: plot the first state.
#            M = u[:,0]
#        elif self.StateName == ['Density','XMomentum','YMomentum','Energy']:
#            # Navier-Stokes equation set
#            gam = 1.4
#            gmi = gam-1
#            # Flow speed
#            q = np.sqrt(u[:,1]**2 + u[:,2]**2) / u[:,0]
#            # Pressure
#            p = gmi * (u[:,-1] -0.4*q*q*u[:,0])
#            # Check for scalar name
#            if scalar.lower() == "mach":
#                # Sound speed
#                c = np.sqrt(gam * p / u[:,0])
#                # Mach number
#                M = q / c
#            elif scalar.lower() == "entropy":
#                # Entropy
#                M = r/gmi * (np.log(p) - gam*np.log(u[:,0]))
#            elif scalar.lower() == "pressure":
#                M = p
#            else:
#                raise RuntimeError((
#                    "Unrecognized Navier-Stokes scalar name '%s'" % scalar))
#        elif self.StateName == [
#                'Density','XMomentum','YMomentum','ZMomentum','Energy']:
#            # Navier-Stokes equation set
#            gam = 1.4
#            gmi = gam-1
#            # Flow speed
#            q = np.sqrt(u[:,1]**2 + u[:,2]**2 + u[:,3]**2) / u[:,0]
#            # Pressure
#            p = gmi * (u[:,-1] -0.4*q*q*u[:,0])
#            # Check for scalar name
#            if scalar.lower() == "mach":
#                # Sound speed
#                c = np.sqrt(gam * p / u[:,0])
#                # Mach number
#                M = q / c
#            elif scalar.lower() == "entropy":
#                # Entropy
#                M = r/gmi * (np.log(p) - gam*np.log(u[:,0]))
#            elif scalar.lower() == "pressure":
#                M = p
#            else:
#                raise RuntimeError((
#                    "Unrecognized Navier-Stokes scalar name '%s'" % scalar))
#        else:
#            raise NotImplementedError("Equation set not implemented.")
#            
#        # Output
#        return M


# ---- Class for xf_GenArray ----
class xf_GenArray:
    """A Python class for XFlow xf_GenArray objects"""
    
    # Initialization method
    def __init__(self, ptr):
        """
        GA = xf_GenArray(ptr)
        
        INPUTS:
           ptr : pointer to xf_GenArray
           
        OUTPUTS:
           GA  : instance of xf_GenArray class
        
        This function creates an xf_GenArray instance, which holds the actual
        data of most xf_Vector structs.
        """
        # Versions:
        #  2013-09-26 @dalle   : First version
        
        # Check the pointer.
        if ptr is None:
            raise NameError
        # Set the pointer.
        self._ptr = ptr
        # Get the GenArray info from the API.
        GA = px.GetGenArray(ptr)
        # Assign the parameters.
        # Number of elements in element group
        self.n = GA["n"]
        # Number of (fixed) degrees of freedom per element
        self.r = GA["r"]
        # Number of (variable) degrees of freedom per element
        self.vr = GA["vr"]
        # Integer data
        self.iValue = GA["iValue"]
        # Real data
        self.rValue = GA["rValue"]
