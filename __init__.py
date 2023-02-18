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
    time: StringProperty(
        name='Time',
        description='Time for FT',
        default=''
    )
    selection_only_for_optimisation: BoolProperty(
        name='Only selected objects',
        description='Check if you want to affect only selected objects',
        default=True,
    )
    selection_only_for_uv_set: BoolProperty(
        name='Only selected objects',
        description='Check if you want to affect only selected objects',
        default=True,
    )
    selection_only_for_mesh_removal: BoolProperty(
        name='Only selected objects',
        description='Check if you want to affect only selected objects',
        default=True,
    )
    remove_mesh_with_no_material: BoolProperty(
        name='No materials',
        description='Check if you want to remove objects with no materials',
        default=True,
    )
    remove_mesh_with_no_uv: BoolProperty(
        name='No UV',
        description='Check if you want to remove objects with no YVs',
        default=True,
    )
    desired_uv_map: StringProperty(
        name='Desired UV',
        description='Enter desired UV',
        default=''
    )


# operators ------------------------------------------------------------------------------------------------------------

class FT_OT_optimise_objects(Operator):
    bl_idname = "ft.optimise_objects"
    bl_label = "Optimise objects"

    def execute(self, context):
        props = context.scene.ft_props
        if props.selection_only_for_optimisation:
            objects = [ob for ob in context.selected_objects if ob.type == 'MESH']
        else:
            objects = [ob for ob in bpy.data.objects if ob.type == 'MESH']

        if not objects:
            self.report({'WARNING'}, 'Nothing to optimise')
            return {'CANCELLED'}

        # active object MUST be 'MESH' type, otherwise an exception occurs (context is incorrect)
        # ask a question to somebody, why this happens???
        context.view_layer.objects.active = objects[0]

        # think how to optimise this
        bpy.ops.object.select_all(action='DESELECT')
        for ob_count, ob in enumerate(objects, start=1):
            ob.select_set(True)
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
                bpy.ops.object.shade_smooth(use_auto_smooth=True)
            ob.select_set(False)

        if ob_count == 1:
            self.report({'INFO'}, f'{ob_count} mesh object successfully optimised')
        else:
            self.report({'INFO'}, f'{ob_count} mesh objects successfully optimised')

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


class FT_OT_test(Operator):
    bl_idname = "ft.test"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Test opearator"

    def execute(self, context):
        print('[DBDMI]: Test operator executed')
        self.report({'INFO'}, 'Test operator executed')
        return {'FINISHED'}


class FT_OT_time_update(Operator):
    bl_idname = "ft.time_update"
    bl_label = "Update time"

    def execute(self, context):
        props = context.scene.ft_props

        current_time = datetime.datetime.now()
        props.time = current_time.strftime("%Y %b %d, %H:%M:%S")

        return {'FINISHED'}


class FT_OT_remove_mesh_without_something(Operator):
    bl_idname = "ft.remove_meshes_without_something"
    bl_label = "Remove mesh"

    def execute(self, context):
        props = context.scene.ft_props
        if props.selection_only_for_mesh_removal:
            objects = [ob for ob in context.selected_objects if ob.type == 'MESH']
        else:
            objects = [ob for ob in bpy.data.objects if ob.type == 'MESH']

        bpy.ops.object.select_all(action='DESELECT')

        for ob in objects:
            if props.remove_mesh_with_no_material and not list(ob.material_slots):
                ob.select_set(True)
                bpy.ops.object.delete(use_global=True)
                continue
            if props.remove_mesh_with_no_uv and not list(ob.data.uv_layers):
                ob.select_set(True)
                bpy.ops.object.delete(use_global=True)

        return {'FINISHED'}


class FT_OT_fix_rotation(Operator):
    bl_idname = "ft.fix_rotation"
    bl_label = "Fix rotation"

    def execute(self, context):
        bpy.ops.view3d.view_axis(type='TOP', align_active=True)
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='VIEW')
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)

        bpy.ops.object.rotation_clear(clear_delta=False)
        bpy.ops.object.location_clear(clear_delta=False)
        bpy.ops.object.scale_clear(clear_delta=False)
        bpy.context.object.rotation_euler[0] = -1.5708

        return {'FINISHED'}


class FT_OT_fix_scale(Operator):
    bl_idname = "ft.fix_scale"
    bl_label = "Fix scale"

    def execute(self, context):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.transform.resize(value=(0.01, 0.01, 0.01))
        bpy.ops.view3d.view_all(center=False)
        return {'FINISHED'}


class FT_OT_fix_x_axis_mirror(Operator):
    bl_idname = "ft.fix_x_axis_mirror"
    bl_label = "Fix X-axis mirror"

    def execute(self, context):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.transform.resize(value=(-1, 1, 1), orient_type='GLOBAL',
                                 orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                 constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False,
                                 proportional_edit_falloff='SMOOTH', proportional_size=1,
                                 use_proportional_connected=False, use_proportional_projected=False, snap=False,
                                 snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST',
                                 use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True,
                                 use_snap_selectable=False)
        return {'FINISHED'}


class FT_OT_use_as_ground(Operator):
    bl_idname = "ft.use_as_ground"
    bl_label = "Use as ground"

    def execute(self, context):
        object = context.active_object
        # enter edit mode
        bpy.ops.object.editmode_toggle()

        # select all verts
        bpy.ops.mesh.select_all(action='SELECT')

        # snap 3D cursor to selected
        bpy.ops.view3d.snap_cursor_to_selected()

        # ezit edit mode
        bpy.ops.object.editmode_toggle()

        # set origin to 3D cursor
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        # save inverse location
        location = object.location * -1

        # clear location
        bpy.ops.object.location_clear(clear_delta=False)

        # select all other objects
        bpy.ops.object.select_all(action='INVERT')
        bpy.ops.transform.translate(value=location)

        return {'FINISHED'}


class FT_OT_set_desired_uv(Operator):
    bl_idname = "ft.set_desired_uv"
    bl_label = "Set desired UV"

    def execute(self, context):
        props = context.scene.ft_props

        if props.selection_only_for_uv_set:
            objects = [ob for ob in context.selected_objects if ob.type == 'MESH']
        else:
            objects = [ob for ob in bpy.data.objects if ob.type == 'MESH']

        bpy.ops.object.select_all(action='DESELECT')

        if not objects:
            self.report({'WARNING'}, 'Nothing to do')
            return {'CANCELLED'}
            # active object MUST be 'MESH' type, otherwise an exception occurs (context is incorrect)
            # ask a question to somebody, why this happens???
        context.view_layer.objects.active = objects[0]

        for ob in objects:
            uv_layers_names = [uv.name for uv in ob.data.uv_layers]
            if props.desired_uv_map in uv_layers_names:
                ob.data.uv_layers[props.desired_uv_map].active = True
                ob.data.uv_layers[props.desired_uv_map].active_render = True

        return {'FINISHED'}


# operators end


# panels ---------------------------------------------------------------------------------------------------------------
class FT_common_panel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FT'


class FT_PT_ninja_ripper(FT_common_panel, Panel):
    bl_label = 'Ninja ripper output fix'

    def draw(self, context):
        layout = self.layout
        props = context.scene.ft_props

        row = layout.row()
        row.operator('ft.fix_rotation')

        row = layout.row()
        row.operator('ft.fix_x_axis_mirror')

        row = layout.row()
        row.operator('ft.use_as_ground')

        row = layout.row()
        row.operator('ft.fix_scale')

        row = layout.row()
        if props.selection_only_for_mesh_removal:
            objects = [ob for ob in context.selected_objects if ob.type == "MESH"]
        else:
            objects = [ob for ob in bpy.data.objects if ob.type == "MESH"]
        text = f'Only selected objects ({len(objects)})'
        row.prop(props, 'selection_only_for_mesh_removal', text=text)

        row = layout.row()
        row.prop(props, 'remove_mesh_with_no_material')

        row = layout.row()
        row.prop(props, 'remove_mesh_with_no_uv')

        row = layout.row()
        row.operator('ft.remove_meshes_without_something')

        row = layout.row()

        row.prop(props, 'desired_uv_map')

        row = layout.row()
        if props.selection_only_for_uv_set:
            objects = [ob for ob in context.selected_objects if ob.type == "MESH"]
        else:
            objects = [ob for ob in bpy.data.objects if ob.type == "MESH"]
        text = f'Only selected objects ({len(objects)})'
        row.prop(props, 'selection_only_for_uv_set', text=text)

        row.operator('ft.set_desired_uv')


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
        row.operator('ft.reset_opt_params')

        row = layout.row()
        row.scale_y = 1.5
        row.prop(props, 'selection_only_for_optimisation')
        if props.selection_only_for_optimisation:
            objects = [ob for ob in context.selected_objects if ob.type == "MESH"]
        else:
            objects = [ob for ob in bpy.data.objects if ob.type == "MESH"]
        if not len(objects):
            text = 'No objects'
        else:
            text = f'Optimise ({len(objects)}) objects'
        row.operator('ft.optimise_objects', text=text, icon='SELECT_EXTEND')


class FT_PT_mesh_translation(FT_common_panel, Panel):
    bl_label = 'Object translation'

    def draw(self, context):
        props = context.scene.ft_props
        layout = self.layout

        row = layout.row()
        row.label(text='Change LocRotScale of selected objects to active object')

        if context.active_object:
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
        row.operator('ft.test')

        row = layout.row()
        row.operator('ft.time_update')

        row = layout.row()
        row.label(text=f'Last updated: {props.time}', icon='TEMP')


# panels end
classes = [
    FT_scene_props,
    FT_OT_optimise_objects,
    FT_OT_reset_opt_params,
    FT_OT_loc_rot_scale_to_active_object,
    FT_OT_test,
    FT_OT_time_update,
    FT_OT_remove_mesh_without_something,
    FT_OT_fix_rotation,
    FT_OT_fix_scale,
    FT_OT_fix_x_axis_mirror,
    FT_OT_use_as_ground,
    FT_OT_set_desired_uv,
    FT_PT_mesh_optimisation,
    FT_PT_mesh_translation,
    FT_PT_test,
    FT_PT_ninja_ripper,
]


def register():
    for cl in classes:
        register_class(cl)

    Scene.ft_props = PointerProperty(type=FT_scene_props)


def unregister():
    del Scene.ft_props

    for cl in reversed(classes):
        unregister_class(cl)
