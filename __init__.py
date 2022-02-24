# by Frutto

from . import mesh_optimiser

bl_info = {
    "name": "Mesh Optimiser",
    "author": "Frutto",
    "version": (1, 0, 0),
    "blender": (3, 0, 1),
    "location": "3D View > Properties > Mesh Optimiser",
    "description": "Simple Mesh Optimiser addon",
    "warning": "",
    "doc_url": "https://github.com/Frutto-Hub/Mesh-Optimiser",
    "category": "Object",
    "support": "COMMUNITY"
}

def register():
    mesh_optimiser.register()

def unregister():
    mesh_optimiser.unregister()

print("Mesh Optimiser add-on loaded")
