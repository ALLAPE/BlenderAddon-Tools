import bpy
import bmesh
from mathutils import Vector

bl_info = {
    "name": "Precise Tools",
    "description": "For accurate operations",
    "author": "ALLAPE",
    # "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "category": "Object",
}

# region tools


def get_selected_vertices(context):
    """
    获取当前对象被选中的点
    get all selected vertices of current selected mesh
    :return tuple
    """
    obj = context.active_object
    if obj.type != 'MESH':
        return list()
    mode = obj.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    selected_vertices = [v for v in obj.data.vertices if v.select]
    bpy.ops.object.mode_set(mode=mode)
    return selected_vertices


# endregion

# region ops


class PutOriginToCenterOp(bpy.types.Operator):
    """Set origin to the center of two selected vertices"""
    bl_idname = "object.to_the_center_of_two_selected_vertices"
    bl_label = "Set origin to the center"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH'

    def execute(self, context):
        selected_vertices = get_selected_vertices(context)

        if len(selected_vertices) < 2:
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


class SplitEdgesOp(bpy.types.Operator):
    """Put a vertex between selected edges"""
    bl_idname = "mesh.split_selected_edges_half"
    bl_label = "Split selected edges half"
    bl_options = {'REGISTER', 'UNDO'}

    position: bpy.props.FloatProperty(
        name="Position",
        description="Position of vertex",
        min=0,
        max=1,
        step=1,
        default=0.5
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH'

    def execute(self, context):
        obj = context.active_object

        me = obj.data
        bme = bmesh.from_edit_mesh(me)

        selected_edges = [e for e in bme.edges if e.select]

        if len(selected_edges) < 1:
            self.report({'INFO'}, 'No edges selected')
            return {'CANCELLED'}

        for edge in selected_edges:
            # (new_edge, vert) =
            bmesh.utils.edge_split(edge, edge.verts[0], self.position)
            # edge.verts[0].select = False
            # edge.verts[1].select = False
            # new_edge.verts[0].select = False
            # new_edge.verts[1].select = False
            # vert.select = True

        bmesh.update_edit_mesh(me)

        # mode = obj.mode
        # bpy.ops.object.mode_set(mode='OBJECT')
        # bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}


# endregion


class PreciseToolsPanel(bpy.types.Panel):
    """Precise Tools"""
    bl_label = "Precise Tools"
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
        row.separator()

        row = layout.row()
        row.label(text="Origin Tools")

        row = layout.row()
        row.operator(PutOriginToCenterOp.bl_idname)

        row = layout.row()
        row.separator()

        row = layout.row()
        row.label(text="Edges Tools")

        row = layout.row()
        row.operator(SplitEdgesOp.bl_idname)


def register():
    bpy.utils.register_class(PreciseToolsPanel)
    bpy.utils.register_class(PutOriginToCenterOp)
    bpy.utils.register_class(SplitEdgesOp)


def unregister():
    bpy.utils.unregister_class(SplitEdgesOp)
    bpy.utils.unregister_class(PutOriginToCenterOp)
    bpy.utils.unregister_class(PreciseToolsPanel)


if __name__ == "__main__":
    register()
