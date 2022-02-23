import bpy, time
from bpy.types import Operator, Panel, PropertyGroup
from bpy.utils import register_class, unregister_class
from bpy.props import PointerProperty, FloatProperty

#t1 = time.perf_counter()

class MeshOptimiserProperties(PropertyGroup):
    auto_smooth_angle: FloatProperty(
        name='Auto smooth angle',
        default=1.0472,
        min=0,
        max=3.14159,
        subtype = 'ANGLE'
    )

class MESH_PT_OPTIMISER(Panel):
    bl_idname = "mesh.optimise"
    bl_label = "Mesh optimise"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mesh Optimiser"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        props = context.scene.mo_props

        row = layout.row()
        row.prop(props, "auto_smooth_angle")

        row = layout.row()
        row.operator('object.optimise')

class MESH_OT_OPTIMISER(Operator):
    bl_idname = 'object.optimise'
    bl_label = 'Optimise Mesh'
    auto_smooth_angle = None

    @classmethod
    def poll(self, context):
        return context.object is not None

    def structure(self, context):
        props = context.scene.mo_props
        self.auto_smooth_angle = props.auto_smooth_angle
        self.scene = context.scene

    def optimise(self, context):
        for obj in bpy.context.selected_objects:
            if bpy.data.objects[obj.name].type == 'MESH':
                bpy.ops.object.editmode_toggle()

                bpy.ops.mesh.select_all(action='SELECT')

                bpy.ops.mesh.remove_doubles(threshold=0.0001)

                bpy.ops.mesh.tris_convert_to_quads(uvs=True)

                bpy.ops.mesh.select_all(action='DESELECT')

                bpy.ops.object.editmode_toggle()

                bpy.ops.object.shade_smooth()

                bpy.data.meshes[obj.data.name].use_auto_smooth = True

                bpy.data.meshes[obj.data.name].auto_smooth_angle = self.auto_smooth_angle

    def execute(self, context):
        self.structure(context)
        self.optimise(context)
        return {'FINISHED'}

# t2 = time.perf_counter()
# print(t2 - t1)

classes = [
    MeshOptimiserProperties,
    MESH_OT_OPTIMISER,
    MESH_PT_OPTIMISER
]

def register():
    for cl in classes:
        register_class(cl)
        bpy.types.Scene.mo_props = PointerProperty(type = MeshOptimiserProperties)

def unregister():
    for cl in reversed(classes):
        unregister_class(cl)

if __name__ == '__main__':
    register()
