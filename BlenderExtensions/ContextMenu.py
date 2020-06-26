# Add some right click options

# stdlib imports
from copy import copy

# Local imports
from ..utils.misc import get_root_node, clone_node

# Blender imports
import bmesh
import bpy
from bpy.types import Menu, Operator
from mathutils import Matrix


class AddReferenceNode(Operator):
    """Add a new NMS reference node"""
    bl_idname = "nmsdk.add_reference_node"
    bl_label = "Reference Node"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        selected_objs = getattr(context, "selected_objects", None)
        if not selected_objs:
            return {'FINISHED'}
        # Create a new empty reference node.
        for obj in selected_objs:
            empty_mesh = bpy.data.meshes.new('ref')
            empty_obj = bpy.data.objects.new('ref', empty_mesh)
            empty_obj.NMSNode_props.node_types = 'Reference'
            empty_obj.matrix_world = Matrix()
            empty_obj.parent = obj
            empty_obj.rotation_mode = 'QUATERNION'
            bpy.context.scene.collection.objects.link(empty_obj)

        return {'FINISHED'}


class AddLocatorNode(Operator):
    """Add a new NMS reference node"""
    bl_idname = "nmsdk.add_locator_node"
    bl_label = "Locator Node"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        selected_objs = getattr(context, "selected_objects", None)
        if not selected_objs:
            return {'FINISHED'}
        # Create a new empty reference node.
        for obj in selected_objs:
            empty_mesh = bpy.data.meshes.new('loc')
            empty_obj = bpy.data.objects.new('loc', empty_mesh)
            empty_obj.NMSNode_props.node_types = 'Locator'
            empty_obj.matrix_world = Matrix()
            empty_obj.parent = obj
            empty_obj.rotation_mode = 'QUATERNION'
            bpy.context.scene.collection.objects.link(empty_obj)

        return {'FINISHED'}


class AddBoxCollisionNode(Operator):
    """Add a new NMS cube mesh node"""
    bl_idname = "nmsdk.add_box_collision_node"
    bl_label = "Cube Mesh node"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        selected_objs = getattr(context, "selected_objects", None)
        if not selected_objs:
            return {'FINISHED'}
        # Create a new empty reference node.
        for obj in selected_objs:
            # Create a new cube for collisions
            mesh = bpy.data.meshes.new('cube')
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=1.0)
            bm.to_mesh(mesh)
            bm.free()
            cube = bpy.data.objects.new('cube', mesh)
            cube.NMSNode_props.node_types = 'Collision'
            cube.NMSCollision_props.collision_types = 'Box'
            cube.matrix_world = Matrix()
            cube.parent = obj
            bpy.context.scene.collection.objects.link(cube)
            cube.rotation_mode = 'QUATERNION'

        return {'FINISHED'}


class CloneNodes(Operator):
    """Clone the selcted node(s)"""
    bl_idname = "nmsdk.clone_nodes"
    bl_label = "Clone node(s)"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        selected_objs = getattr(context, "selected_objects", None)
        if not selected_objs:
            return {'FINISHED'}
        # Make a copy of each of the selected nodes.
        for obj in selected_objs:
            clone_node(obj)
        return {'FINISHED'}


class CloneNodesRecursively(Operator):
    """Clone the selcted node(s) and all attached children"""
    bl_idname = "nmsdk.clone_nodes_recursively"
    bl_label = "Clone node(s) recursively"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        selected_objs = getattr(context, "selected_objects", None)
        if not selected_objs:
            return {'FINISHED'}
        # Make a copy of each of the selected nodes.
        for obj in selected_objs:
            clone_node(obj, True)
        return {'FINISHED'}


class WM_OT_button_add_parent(Operator):
    """ Add the selected objects as child nodes to the selected parent"""
    bl_idname = "wm.add_to_parent"
    bl_label = "Add object to NMSDK scene"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        selected_objs = getattr(context, "selected_objects", None)
        parent_obj = getattr(context, "active_object", None)
        root_obj = get_root_node(parent_obj)
        for obj in selected_objs:
            print(obj)
            if obj == parent_obj:
                # Skip over the parent obj.
                pass
            # 1. copy the world matrix of the object.
            trans = copy(obj.matrix_world)
            # 2. Set the world matrix of the object to be the Identity matrix.
            obj.matrix_world = Matrix()
            # 3. Change the object to be in the coordinate system of the root
            # node. Apply this change the object.
            obj.data.transform(root_obj.matrix_world)
            obj.matrix_world = Matrix()
            # 4. Parent the object to the required object.
            obj.parent = parent_obj
            # 5. Set the objects transform from before.
            obj.matrix_local = trans

        return {'FINISHED'}


class NMSDK_MT_add_NMS_Scenenodes(Menu):
    bl_label = "Add new Scene Node objects"
    bl_idname = "NMSDK_MT_add_NMS_Scenenodes"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('nmsdk.add_reference_node')
        row = layout.row()
        row.operator('nmsdk.add_locator_node')
        row = layout.row()
        row.operator('nmsdk.add_box_collision_node')


class NMSDK_MT_clone_NMS_Scenenodes(Menu):
    bl_label = "Clone NMS Scenenode objects"
    bl_idname = "NMSDK_MT_clone_NMS_Scenenodes"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('nmsdk.clone_nodes')
        row = layout.row()
        row.operator('nmsdk.clone_nodes_recursively')
        row = layout.row()


# Functions to modify blenders' menu items


def add_empty_root_node(self, context):
    """ Add an option to the 'add' menu in the 3D view to add an empty root
    NMS SceneNode reference for exporting. """
    layout = self.layout
    layout.separator()
    layout.operator('nmsdk.create_root_scene')


def parent_menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator('wm.add_to_parent')


def add_obj_menu_func(self, context):
    """ Add the sub-menu to the context menu. """
    layout = self.layout
    layout.separator()
    row = layout.row()
    row.menu("NMSDK_MT_add_NMS_Scenenodes")
    row = layout.row()
    row.menu("NMSDK_MT_clone_NMS_Scenenodes")


classes = (WM_OT_button_add_parent,
           AddReferenceNode,
           AddBoxCollisionNode,
           AddLocatorNode,
           NMSDK_MT_add_NMS_Scenenodes,
           NMSDK_MT_clone_NMS_Scenenodes,
           CloneNodes,
           CloneNodesRecursively)


class ContextMenus():
    @staticmethod
    def register():
        # Register classes to be used.
        for cls_ in classes:
            bpy.utils.register_class(cls_)
        # Add the functions to the menus they need to be in.
        bpy.types.VIEW3D_MT_add.append(add_empty_root_node)
        bpy.types.VIEW3D_MT_object_parent.append(parent_menu_func)
        bpy.types.VIEW3D_MT_object_context_menu.append(add_obj_menu_func)

    @staticmethod
    def unregister():
        # Unregister classes used.
        for cls_ in classes:
            bpy.utils.unregister_class(cls_)
        # Remove the functions from the menus they were in.
        bpy.types.VIEW3D_MT_add.remove(add_empty_root_node)
        bpy.types.VIEW3D_MT_object_parent.remove(parent_menu_func)
        bpy.types.VIEW3D_MT_object_context_menu.remove(add_obj_menu_func)
