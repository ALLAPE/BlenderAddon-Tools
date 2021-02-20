import bpy
from mathutils import Vector, Matrix


def get_selected_vertices(context):
    mode = context.active_object.mode
    # we need to switch from Edit mode to Object mode so the selection gets updated
    bpy.ops.object.mode_set(mode='OBJECT')
    selected_vertices = [v for v in context.active_object.data.vertices if v.select]
    # back to whatever mode we were in
    bpy.ops.object.mode_set(mode=mode)
    return selected_vertices


class PutOriginToCenter(bpy.types.Operator):
    """Set origin to the center of selected vertices"""
    bl_idname = "object.to_the_center_of_two_selected_vertices"
    bl_label = "Set origin to the center"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH'

    def execute(self, context):
        selected_vertices = get_selected_vertices(context)

        if len(get_selected_vertices(context)) < 2:
            self.report({'INFO'}, 'At least two vertices selected')
            return {'FINISHED'}

        obj = context.active_object
        mode = context.active_object.mode

        bpy.ops.object.mode_set(mode='OBJECT')

        # saved cursor location
        cursor_location = tuple(context.scene.cursor.location)

        vertex1_location = obj.matrix_world @ selected_vertices[0].co
        vertex2_location = obj.matrix_world @ selected_vertices[1].co

        context.scene.cursor.location = Vector((
            (vertex1_location[0] + vertex2_location[0]) / 2,
            (vertex1_location[1] + vertex2_location[1]) / 2,
            (vertex1_location[2] + vertex2_location[2]) / 2,
        ))
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        context.scene.cursor.location = Vector(cursor_location)

        bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}


class OriginToolsPanel(bpy.types.Panel):
    """Origin Tools"""
    bl_label = "Origin Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_context = "mesh_edit"

    def draw(self, context):
        obj = context.object

        layout = self.layout

        row = layout.row()
        row.label(text="Active object is: {}".format(obj.name))
        row = layout.row()
        row.operator(PutOriginToCenter.bl_idname)


def register():
    bpy.utils.register_class(OriginToolsPanel)
    bpy.utils.register_class(PutOriginToCenter)


def unregister():
    bpy.utils.unregister_class(PutOriginToCenter)
    bpy.utils.unregister_class(OriginToolsPanel)


if __name__ == "__main__":
    register()
