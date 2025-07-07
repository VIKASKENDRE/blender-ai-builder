bl_info = {
    "name": "AI Builder",
    "author": "Your Name",
    "version": (0, 1),
    "blender": (4, 4, 0),
    "location": "View3D > Sidebar > AI Builder",
    "description": "Generate objects from text instructions",
    "category": "Object",
}

import bpy
import requests
import ast

# ---------- Operator ----------

class OBJECT_OT_ai_builder(bpy.types.Operator):
    """Parses text input with OpenAI and creates objects"""
    bl_idname = "object.ai_builder"
    bl_label = "AI Build"

    def execute(self, context):
        prompt = context.scene.ai_builder_prompt

        # Call OpenAI GPT to parse prompt
        parsed_objects = self.call_openai(prompt)

        # Process parsed objects
        for obj in parsed_objects:
            name = obj.get("name")
            if name == "room":
                self.create_room()
            elif name == "desk":
                self.create_desk()
            elif name == "lamp":
                self.create_lamp()
            else:
                self.report({'WARNING'}, f"Unknown object: {name}")

        self.report({'INFO'}, "AI Build completed.")
        return {'FINISHED'}

    def call_local_llm(prompt):
        url = "http://127.0.0.1:8000/parse"
        system_prompt = (
            "You are a helpful assistant that extracts structured object data "
            "from user scene creation instructions. "
            "Return output as a JSON list of objects with 'name' field. "
            "For example: [{'name': 'room'}, {'name': 'desk'}, {'name': 'lamp'}]"
        )
        full_prompt = f"{system_prompt}\n\nInstruction: {prompt}"

        try:
            response = requests.post(url, json={"prompt": full_prompt})
            if response.status_code == 200:
                data = response.json()
                parsed_objects = ast.literal_eval(data["result"])
                return parsed_objects
        except Exception as e:
            print(f"LLM server error: {e}")
        return []


    def create_room(self):
        bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
        floor = bpy.context.active_object
        floor.name = "Floor"

        wall_thickness = 0.1
        wall_height = 3

        bpy.ops.mesh.primitive_cube_add(location=(0, -5, wall_height/2))
        back_wall = bpy.context.active_object
        back_wall.scale = (5, wall_thickness, wall_height/2)
        back_wall.name = "Back Wall"

        bpy.ops.mesh.primitive_cube_add(location=(0, 5, wall_height/2))
        front_wall = bpy.context.active_object
        front_wall.scale = (5, wall_thickness, wall_height/2)
        front_wall.name = "Front Wall"

        bpy.ops.mesh.primitive_cube_add(location=(-5, 0, wall_height/2))
        left_wall = bpy.context.active_object
        left_wall.scale = (wall_thickness, 5, wall_height/2)
        left_wall.name = "Left Wall"

        bpy.ops.mesh.primitive_cube_add(location=(5, 0, wall_height/2))
        right_wall = bpy.context.active_object
        right_wall.scale = (wall_thickness, 5, wall_height/2)
        right_wall.name = "Right Wall"

    def create_desk(self):
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
        desk = bpy.context.active_object
        desk.scale = (1, 0.5, 0.05)
        desk.name = "Desk"

    def create_lamp(self):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1, location=(0.5, 0, 1.5))
        stand = bpy.context.active_object
        stand.name = "Lamp Stand"

        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(0.5, 0, 2))
        head = bpy.context.active_object
        head.name = "Lamp Head"

# ---------- Panel ----------

class VIEW3D_PT_ai_builder_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "AI Builder"
    bl_idname = "VIEW3D_PT_ai_builder_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI Builder'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "ai_builder_prompt")
        layout.operator("object.ai_builder", text="Generate Objects")

# ---------- Register ----------

classes = (
    OBJECT_OT_ai_builder,
    VIEW3D_PT_ai_builder_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.ai_builder_prompt = bpy.props.StringProperty(
        name="Prompt",
        description="Describe your scene",
        default=""
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.ai_builder_prompt

if __name__ == "__main__":
    register()
