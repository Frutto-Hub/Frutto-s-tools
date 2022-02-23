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
    "wiki_url": "https://github.com/AnimNyan/UEShaderScript",
    "category": "Object",
    "tracker_url": "https://github.com/AnimNyan/UEShaderScript"
}

def register():
    mesh_optimiser.register()

def unregister():
    mesh_optimiser.unregister()

print("Mesh Optimiser add-on loaded")
