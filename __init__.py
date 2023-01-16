bl_info = {
    'name': "Frutto's tools",
    'blender': (3, 4, 0),
    'category': 'Object',
    "author": "Frutto",
    'version': (1, 0),
    "location": "3D View > Properties > FT",
    "description": "Frutto's Tools for faster working",
    "doc_url": "https://github.com/Frutto-Hub/Mesh-Optimiser",
    'support': 'COMMUNITY',
    'warning': '',
    'show_expanded': False,
    '_init': None,
    'tracker_url': '',
}

import bpy
from bpy.types import Operator, Panel, PropertyGroup, Object, Scene
from bpy.utils import register_class, unregister_class
from bpy.props import PointerProperty, FloatProperty, IntProperty, StringProperty, BoolProperty, EnumProperty

import datetime
from math import pi


# custom ft props --------------------------------------------------------------------------------------------------
class FT_scene_props(PropertyGroup):
    remove_doubles_enabled: BoolProperty(
        name='Remove double vertices',
        description='Remove double vertices (Remove vertices same coordinates)',
        default=True,
    )
    merge_distance: FloatProperty(
        name='Merge distance',
        default=0.0001,
        min=0,
        max=1,
    )
    to_quads_enabled: BoolProperty(
        name='Triangles to quads',
        description='Change triangles to quads',
        default=True,
    )
    max_face_angle: FloatProperty(
        name='Max face angle',
        default=40 * (pi / 180),
        min=0,
        max=180 * (pi / 180),
        subtype='ANGLE'
    )
    max_shape_angle: FloatProperty(
        name='Max shape angle',
        default=40 * (pi / 180),
        min=0,
        max=180 * (pi / 180),
        subtype='ANGLE'
    )
    shade_smooth_enabled: BoolProperty(
        name='Shade smooth',
        description='Make shade smooth',
        default=True,
    )

    smooth_angle: FloatProperty(
        name='Smooth angle',
        default=1.0472,
        min=0,
        max=180 * (pi / 180),
        subtype='ANGLE'
    )

    apply_loc_rot_scale: BoolProperty(
        name='Apply LocRocScale after translation',
        description='Apply LocRocScale after translation',
        default=True,
    )


# operators ------------------------------------------------------------------------------------------------------------

class FT_OT_mesh_optimisation(Operator):
    bl_idname = "ft.optimise_mesh"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Optimise Mesh"

    def execute(self, context):
        props = context.scene.ft_props
        selected_mesh = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if selected_mesh:
            # active object MUST be 'MESH' type, otherwise an exception occurs (context is incorrect)
            # ask a question to somebody, why this happens???
            context.view_layer.objects.active = selected_mesh[0]
        else:
            self.report({'WARNING'}, 'Nothing to optimise')
            return {'CANCELLED'}

        # think how to optimise this
        bpy.ops.object.select_all(action='DESELECT')
        for objects_optimised, obj in enumerate(selected_mesh, 1):
            if props.remove_doubles_enabled:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles(threshold=props.merge_distance)
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.editmode_toggle()

            if props.to_quads_enabled:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.tris_convert_to_quads(uvs=True)
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.editmode_toggle()

            if props.shade_smooth_enabled:
                obj.select_set(True)
                bpy.ops.object.shade_smooth(use_auto_smooth=True)
                obj.select_set(False)

        # selecting back mesh objects
        for obj in selected_mesh:
            obj.select_set(True)

        if objects_optimised == 1:
            self.report({'INFO'}, f'{objects_optimised} mesh object successfully optimised')
        else:
            self.report({'INFO'}, f'{objects_optimised} mesh objects successfully optimised')
        print('[DBDMI]: Mesh optimised executed')

        return {'FINISHED'}


class FT_OT_reset_opt_params(Operator):
    bl_idname = "ft.reset_opt_params"
    bl_label = "Reset optimisation parameters"

    def execute(self, context):
        props = context.scene.ft_props
        props.remove_doubles_enabled = True
        props.merge_distance = 0.0001
        props.to_quads_enabled = True
        props.max_face_angle = 40 * (pi / 180)
        props.max_shape_angle = 40 * (pi / 180)
        props.shade_smooth_enabled = True
        props.smooth_angle = 1.0472

        self.report({'INFO'}, 'Optimisation parameters reset')
        return {'FINISHED'}


class FT_OT_loc_rot_scale_to_active_object(Operator):
    bl_idname = "ft.loc_rot_scale_to_active_object"
    bl_label = "Translate to active object"

    def execute(self, context):
        props = context.scene.ft_props
        active_obj = context.active_object
        selected_objects = context.selected_objects
        selected_objects_without_active = set(selected_objects).difference({active_obj})
        print(f'source_obj = {selected_objects_without_active}')
        print(f'active_obj = {active_obj}')

        ## debug, doesn't work
        for ob in selected_objects_without_active:
            ob.location = active_obj.location
            ob.rotation_euler = active_obj.rotation_euler
            ob.scale = active_obj.scale
            if props.apply_loc_rot_scale:
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        self.report({'INFO'}, 'Loc Rot Scale transferred to active object')
        return {'FINISHED'}


class FT_OT_Test(Operator):
    bl_idname = "ft.test"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Test opearator"

    def execute(self, context):
        print('[DBDMI]: Test operator executed')
        self.report({'INFO'}, 'Test operator executed')
        return {'FINISHED'}


class FT_OT_time_update(Operator):
    bl_idname = "ft.test_time"
    bl_label = "Update time"

    def execute(self, context):
        props = context.scene.ft_props

        current_time = datetime.datetime.now()
        props.last_database_updated = current_time.strftime("%Y %b %d, %H:%M:%S")

        return {'FINISHED'}


# operators end


# panels ---------------------------------------------------------------------------------------------------------------
class FT_common_panel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FT'


class FT_PT_mesh_optimisation(FT_common_panel, Panel):
    bl_label = 'Mesh optimisation'

    def draw(self, context):
        layout = self.layout
        props = context.scene.ft_props

        row = layout.row()
        row.prop(props, 'remove_doubles_enabled')

        if props.remove_doubles_enabled:
            row = layout.row()
            row.prop(props, 'merge_distance')

        row = layout.row()
        row.prop(props, 'to_quads_enabled')

        if props.to_quads_enabled:
            row = layout.row()
            row.prop(props, 'max_face_angle')

            row = layout.row()
            row.prop(props, 'max_shape_angle')

        row = layout.row()
        row.prop(props, 'shade_smooth_enabled')

        if props.shade_smooth_enabled:
            row = layout.row()
            row.prop(props, 'smooth_angle')

        row = layout.row()
        row.label(text=f'Mesh objects selected: {len([obj for obj in context.selected_objects if obj.type == "MESH"])}')
        row.operator('ft.reset_opt_params')

        row = layout.row()
        row.scale_y = 1.5
        row.operator('ft.optimise_mesh')


class FT_PT_mesh_translation(FT_common_panel, Panel):
    bl_label = 'Object translation'

    def draw(self, context):
        props = context.scene.ft_props
        layout = self.layout

        row = layout.row()
        row.label(text='Change LocRotScale of selected objects to active object')

        row = layout.row()
        row.label(text=f'Active object: {context.active_object.name}')

        row = layout.row()
        obj_count = 0 if len(context.selected_objects) == 0 else len(context.selected_objects) - 1
        row.label(text=f'Objects to translate: {obj_count}')

        row = layout.row()
        row.prop(props, 'apply_loc_rot_scale')

        row = layout.row()
        row.operator('ft.loc_rot_scale_to_active_object')


class FT_PT_test(FT_common_panel, Panel):
    bl_label = 'Test_panel'

    def draw(self, context):
        layout = self.layout
        props = context.scene.ft_props

        row = layout.row()
        row.operator('ft.test_time')


# panels end

classes = [
    FT_scene_props,
    FT_OT_mesh_optimisation,
    FT_OT_reset_opt_params,
    FT_OT_loc_rot_scale_to_active_object,
    FT_OT_Test,
    FT_OT_time_update,
    FT_PT_mesh_optimisation,
    FT_PT_mesh_translation,
    FT_PT_test,
]


def register():
    for cl in classes:
        register_class(cl)

    Scene.ft_props = PointerProperty(type=FT_scene_props)


def unregister():
    del Scene.ft_props

    for cl in reversed(classes):
        unregister_class(cl)
