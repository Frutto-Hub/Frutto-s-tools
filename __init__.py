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


# custom ft props --------------------------------------------------------------------------------------------------
class FT_scene_props(PropertyGroup):
    auto_smooth_angle: FloatProperty(
        name='Auto smooth angle',
        default=1.0472,
        min=0,
        max=3.14159,
        subtype='ANGLE'
    )

    database_folder: StringProperty(
        name="Database folder set",
        description='Real seted folder for storing all data required for dbdmi addon',
        default='',
        subtype='FILE_PATH'
    )
    pak_folder: StringProperty(
        name="DBD Pak folder set",
        description='DBD Pak files location on your computer',
        default='',
        subtype='FILE_PATH'
    )

    select_import_character_role: EnumProperty(
        name="Select character role",
        items=(('survivour', 'Survivour', 'Select survivour role'),
               ('killer', 'Killer', 'Select killer role')),
        description='Select survivour or killer role',
        default='survivour'
    )

    select_import_character_sex: EnumProperty(
        name="Select survivour sex",
        items=(('male', 'Male', 'Select male character'),
               ('female', 'Female', 'Select female character')),
        description='Select male or female character',
        default='male'
    )

    filter_by_sex: BoolProperty(
        name='Filter by sex',
        description='Filter characters by sex for icons preview',
        default=True,
    )


# operators ------------------------------------------------------------------------------------------------------------
class FT_OT_Test(Operator):
    bl_idname = "dbdmi.test"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Test opearator"

    def execute(self, context):
        print(bpy.path.abspath(path='', start='//'))
        print('[DBDMI]: Test operator executed')
        self.report({'INFO'}, 'Test operator executed')
        return {'FINISHED'}


class FT_OT_optimise_mesh(Operator):
    bl_idname = "ft.optimise_mesh"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Optimise Mesh"

    def execute(self, context):
        selected_mesh = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if selected_mesh:
            # active object MUST be MESH type, otherwise an exception occurs (context is incorrect)
            # ask a question to somebody, why this happens???
            context.view_layer.objects.active = selected_mesh[0]
        else:
            self.report({'WARNING'}, 'Nothing to optimise')
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for objects_optimised, obj in enumerate(selected_mesh, 1):
            print(obj.type)
            # print(f'{i}) obj_name = {obj.name}, obj_type = {obj.type}')
            bpy.ops.object.mode_set(mode='EDIT')

            bpy.ops.mesh.select_all(action='SELECT')

            bpy.ops.mesh.remove_doubles(threshold=0.0001)

            bpy.ops.mesh.tris_convert_to_quads(uvs=True)

            bpy.ops.mesh.select_all(action='DESELECT')

            bpy.ops.object.editmode_toggle()

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


class FT_OT_time_update(Operator):
    bl_idname = "ft.test_time"
    bl_label = "Update time"

    def execute(self, context):
        props = context.scene.ft_props

        current_time = datetime.datetime.now()
        props.last_database_updated = current_time.strftime("%Y %b %d, %H:%M:%S")

        return {'FINISHED'}


class FT_OT_loc_rot_scale_to_active_object(Operator):
    bl_idname = "ft.loc_rot_scale_to_active_object"
    bl_label = "Loc Rot Scale to active object"

    def execute(self, context):
        selected_objs = context.selected_objects

        # check, that exactly two object has beed selected
        if len(selected_objs) < 2:
            self.report({'WARNING'}, 'Not enough objects selected')
            return {'CANCELLED'}
        elif len(selected_objs) > 2:
            self.report({'WARNING'}, 'Too many objects selected')
            return {'CANCELLED'}

        target_obj = context.active_object
        selected_objs = context.selected_objects
        # my_list = [active_obj]
        source_obj = set(selected_objs).difference(set([target_obj]))
        print(f'source_obj = {source_obj}')
        print(f'target_obj = {target_obj}')

        for ob in source_obj:
            ob.location = target_obj.location
            ob.rotation_euler = target_obj.rotation_euler
            ob.scale = target_obj.scale

        self.report({'INFO'}, 'Loc Rot Scale transferred to active object')
        return {'FINISHED'}


# operators end


# panels ---------------------------------------------------------------------------------------------------------------
class FT_common_panel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FT'


class FT_PT_mesh_optimise(FT_common_panel, Panel):
    bl_label = 'Mesh optimisation'

    def draw(self, context):
        layout = self.layout
        props = context.scene.ft_props

        row = layout.row(align=True)
        row.label(text='Select character:')
        row.prop(props, 'filter_by_sex')

        row = layout.row()
        row.prop(props, 'select_import_character_role',
                 expand=True,
                 )
        if props.filter_by_sex:
            row = layout.row()
            row.prop(props, 'select_import_character_sex',
                     expand=True,
                     )

        row = layout.row()

        row = layout.row()
        row.operator('ft.optimise_mesh')

        row = layout.row()
        row.operator('ft.test_time')

        row = layout.row()
        row.label(text=f'Last updated: {props.last_database_updated}', icon='TEMP')

        row = layout.row()
        row.operator('ft.loc_rot_scale_to_active_object')


class FT_PT_mesh_moving(FT_common_panel, Panel):
    bl_label = 'Mesh translation'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text='Settings panel')


class FT_PT_test(FT_common_panel, Panel):
    bl_label = 'Test_panel'

    def draw(self, context):
        layout = self.layout
        props = context.scene.ft_props


class FT_PT_info(FT_common_panel, Panel):
    bl_label = 'Info'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text='Info panel for FT')


# panels end

classes = [
    FT_scene_props,
    FT_OT_optimise_mesh,
    FT_OT_Test,

    FT_PT_info,
    FT_PT_mesh_optimise,
    FT_PT_mesh_moving,
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
