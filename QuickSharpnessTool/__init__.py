bl_info = {
    "name": "Quick Sharpness Tool 2.0",
    "author": "Stas Zvyagintsev",
    "version": (2, 0),
    "blender": (3, 1, 2),
    "location": "N-Panel > QST 2.0",
    "description": "Mark Sharpness",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
from bpy.types import Operator, Panel
from bpy.utils import register_class, unregister_class


class QST_OT_qwick_mark_sharp(bpy.types.Operator):
    bl_idname = "object.simple_operator"
    bl_label = "Mark Sharp"

    def execute(self, context):
        self.to_object_mode(context)
        self.mark_sharp_in_model(context)
        return {'FINISHED'}

    def mark_sharp_in_model(self, context) -> None:
        if len(bpy.context.selected_objects) == 0:
            return None
        for i in bpy.context.selected_objects:
            if i.type == 'MESH':
                bpy.data.objects[i.name].select_set(True)
                bpy.context.view_layer.objects.active = bpy.data.objects[i.name]

                bpy.ops.object.shade_smooth()
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
                bpy.context.object.data.use_auto_smooth = True
                bpy.context.object.data.auto_smooth_angle = 1.0472

                bpy.ops.mesh.customdata_custom_splitnormals_add()
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
                bpy.context.object.data.auto_smooth_angle = 3.14159

    def to_object_mode(self, context) -> None:
        if not bpy.context.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')


class QST_OT_transfer_shading(bpy.types.Operator):
    bl_idname = "object.transfer_shading_operator"
    bl_label = "Transfer shading"

    def execute(self, context):
        QST_OT_transfer_shading.get_data_transfer(context)
        return {'FINISHED'}

    @classmethod
    def get_data_transfer(cls, context) -> None:
        meshes = bpy.context.selected_objects
        bad_shade = bpy.context.active_object if len(bpy.context.selected_objects) > 0 else ''
        good_shading = ''

        for mesh in meshes:
            if not mesh.name == bad_shade.name:
                good_shading = mesh.name

                bpy.ops.object.modifier_add(type='DATA_TRANSFER')
                bpy.context.object.modifiers["DataTransfer"].object = bpy.data.objects[good_shading]
                bpy.context.object.modifiers["DataTransfer"].use_loop_data = True
                bpy.context.object.modifiers["DataTransfer"].data_types_loops = {'CUSTOM_NORMAL'}
                bpy.context.object.modifiers["DataTransfer"].loop_mapping = 'POLYINTERP_LNORPROJ'

        if not good_shading == '':
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[good_shading].select_set(True)
            bpy.ops.object.hide_view_set(unselected=False)


class QST_OT_transfer_shading_and_apply(bpy.types.Operator):
    bl_idname = "object.transfer_shading_operator_and_apply"
    bl_label = "Transfer shading & apply"

    def execute(self, context) -> None:
        QST_OT_transfer_shading.get_data_transfer(context)
        bpy.ops.object.modifier_apply(modifier="DataTransfer")
        return {'FINISHED'}


class QST_PT_qwick_mark_sharp(bpy.types.Panel):
    bl_label = "Mark Sharp"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "QST 2.0"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('object.simple_operator', icon='SNAP_VOLUME')


class QST_PT_transfer_shading(bpy.types.Panel):
    bl_label = "Transfer Shading"
    bl_idname = "OBJECT_PT_TransferShading"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "QST 2.0"

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        if bpy.context.mode == 'OBJECT':
            row.operator('object.transfer_shading_operator')
            row = layout.row()
            row.operator('object.transfer_shading_operator_and_apply')

            active_obj = bpy.context.active_object.name if not bpy.context.active_object == None else ''
            target_obj = ''

            if len(bpy.context.selected_objects) <= 2:
                for i in bpy.context.selected_objects:
                    if not i.name == active_obj:
                        target_obj = i.name

            if len(bpy.context.selected_objects) == 0 or len(bpy.context.selected_objects) > 2:
                row = layout.box()
                row.label(text=f'target: none', icon='RESTRICT_SELECT_ON')
                row.label(text=f'sourse: none', icon='RESTRICT_SELECT_ON')
            elif len(bpy.context.selected_objects) == 1:
                row = layout.box()
                row.label(text=f'target: none', icon='RESTRICT_SELECT_ON')
                row.label(text=f'sourse: {active_obj}', icon='RESTRICT_SELECT_OFF')
            elif len(bpy.context.selected_objects) == 2:
                row = layout.box()
                row.label(text=f'target: {active_obj}', icon='RESTRICT_SELECT_OFF')
                row.label(text=f'sourse: {target_obj}', icon='RESTRICT_SELECT_OFF')
        else:
            row.label(text='only works in object mode', icon='FILE_REFRESH')


classes = (
    QST_OT_qwick_mark_sharp,
    QST_OT_transfer_shading,
    QST_OT_transfer_shading_and_apply,
    QST_PT_qwick_mark_sharp,
    QST_PT_transfer_shading,
)


def register():
    for cl in classes:
        register_class(cl)


def unregister():
    for cl in reversed(classes):
        unregister_class(cl)


if __name__ == "__main__":
    register()
