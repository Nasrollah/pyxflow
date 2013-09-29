#ifndef _PX_MESH_H
#define _PX_MESH_H

PyObject *
px_CreateMesh(PyObject *self, PyObject *args);
/*
PURPOSE:
  Creates an empty xf_Mesh object and returns pointer

CALL:
  M = px.CreateMesh()

INPUTS:
  None

OUTPUTS:
  M : pointer to xf_Mesh
*/


PyObject *
px_ReadGriFile(PyObject *self, PyObject *args);
/*
PURPOSE:
  Reads a GRI file and returns a pointer to xf_Mesh struct

CALL:
  M = px.CreateMesh(fname)

INPUTS:
  fname : GRI file

OUTPUTS:
  M : pointer to xf_Mesh
*/


PyObject *
px_WriteGriFile(PyObject *self, PyObject *args);
/*
PURPOSE:
  Write an xf_Mesh object to a GRI file

CALL:
  px.WriteGriFile(M, fname)

INPUTS:
  M     : xf_Mesh pointer (python int)
  fname : file name for output
  
OUTPUTS:
  None
*/


PyObject *
px_GetNodes(PyObject *self, PyObject *args);
/*
PURPOSE:
  Get basic nodes information from xf_Mesh object
  
CALL:
  (Dim, nNode, Coord) = px.GetNodes(M)

INPUTS:
  M : xf_Mesh pointer
  
OUTPUTS:
  Dim   : number of dimensions [ 2 | 3 ]
  nNode : number of nodes
  Coord : numpy.ndarray of coordinates  [(nNode)x(Dim) ndarray]
*/


PyObject *
px_nBFaceGroup(PyObject *self, PyObject *args);
/*
PURPOSE:
  Get number of boundary conditions
  
CALL:
  nBFG = px.nBFaceGroup(M)

INPUTS:
  M : xf_Mesh pointer

OUTPUTS:
  nBFG : number of xf_BFaceGroup structs in xf_Mesh
*/


PyObject *
px_BFaceGroup(PyObject *self, PyObject *args);
/*
PURPOSE:
  Get basic information from a boundary face group
  
CALL:
  (Title, nBFace, BFG) = px.BFaceGroup(M, iBFG)
  
INPUTS:
  M    : pointer to xf_Mesh
  iBFG : index of boundary face group
  
OUTPUTS:
  Title  : title of BFace group, Mesh->BFaceGroup[i]->Title
  nBFace : number of BFaces in BFaceGroup[i]
  BFG    : pointer to Mesh->BFaceGroup[i]
*/


PyObject *
px_nElemGroup(PyObject *self, PyObject *args);
/*
PURPOSE:
  Get number of element groups and corresponding pointer
  
CALL:
  nEG = px.nElemGroup(M)

INPUTS:
  M : xf_Mesh pointer

OUTPUTS:
  nEG : number of xf_ElemGroup structs in xf_Mesh
*/


PyObject *
px_ElemGroup(PyObject *self, PyObject *args);
/*
PURPOSE:
  Get basic information from an element group
  
CALL:
  (nElem, nNode, QOrder, QBasis, Node) = px.ElemGroup(M i)
  
INPUTS:
  M : pointer to xf_Mesh
  i : index of element group
  
OUTPUTS:
  nElem  : number of elements in group, Mesh->ElemGroup[i].nElem
  nNode  : number of nodes in group, Mesh->ElemGroup[i].nNode
  QOrder : order of elements in group
  QBasis : string describing basis functions
  Node   : int NumPy array of node numbers in each element
*/




PyObject *
px_DestroyMesh(PyObject *self, PyObject *args);
/*
PURPOSE:
  Calls xf_DestroyMesh on the pointer to xf_Mesh struct

CALL:
  px.DestroyMesh(M)

INPUTS:
  M : xf_Mesh pointer

OUTPUTS:
  None
*/

#endif
