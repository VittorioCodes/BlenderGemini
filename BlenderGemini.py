import bpy
import urllib.request
import urllib.error
import textwrap
import json

bl_info = {
    "name": "Blender Gemini",
    "author": "VittorioCodes",
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Gemini AI",
    "description": "State-aware AI Assistant inside Blender",
    "category": "Interface",
}

DEFAULT_API_KEY = "ENTER_YOUR_API_KEY_HERE"

# --- System Instruction ---
SYSTEM_PROMPT = (
    "You are an AI assistant running inside Blender, integrated via an add-on developed by https://github.com/VittorioCodes. "
    "You are helping a 3D artist. You must always assume: "
    "- The user is working inside Blender. "
    "- Solutions must be Blender-specific. "
    "- If code is provided, it must be valid 'bpy' Python code. "
    "- Prefer practical steps and direct solutions over theory. "
    "- Ask for clarification only if absolutely necessary. "
    "While you specialize in Blender modeling, scripting, and rendering, do not limit your knowledge strictly to Blender; "
    "remain a versatile assistant, but always prioritize the context of the 3D workflow."
)

# --- Helper Function: Scene Snapshot ---
def get_blender_context_info(context, props):
    """Gathers current Blender state to provide context for the AI."""
    info = ["--- BLENDER CONTEXT ---"]
    
    if props.ctx_scene:
        info.append(f"Blender Version: {bpy.app.version_string}")
        info.append(f"Render Engine: {context.scene.render.engine}")
        info.append(f"Current Mode: {context.mode}")
    
    obj = context.active_object
    if obj and props.ctx_object:
        info.append(f"Active Object: {obj.name} (Type: {obj.type})")
        info.append(f"Location: {obj.location}")
        
        if obj.type == 'MESH':
            info.append(f"Geometry: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} faces")
            if props.ctx_modifiers:
                mods = [m.name for m in obj.modifiers]
                info.append(f"Modifiers: {mods if mods else 'None'}")
            if props.ctx_materials:
                mats = [slot.material.name for slot in obj.material_slots if slot.material]
                info.append(f"Materials: {mats if mats else 'None'}")
                
    info.append("--- END OF CONTEXT ---")
    return "\n".join(info)

# --- Data Structures ---
class GEMINI_STR_Message(bpy.types.PropertyGroup):
    role: bpy.props.StringProperty()
    content: bpy.props.StringProperty()

class GEMINI_STR_Settings(bpy.types.PropertyGroup):
    free_model_enum: bpy.props.EnumProperty(
        name="Free Model",
        items=[
            ("gemini-2.5-flash", "Gemini 2.5 Flash", ""),
            ("gemini-2.5-flash-lite", "Gemini 2.5 Flash Lite", ""),
            ("gemini-1.5-flash", "Gemini 1.5 Flash", ""),
        ],
        default="gemini-2.5-flash"
    )

    paid_model_enum: bpy.props.EnumProperty(
        name="Pro Model",
        items=[
            ("gemini-2.5-pro", "Gemini 2.5 Pro", ""),
            ("gemini-1.5-pro", "Gemini 1.5 Pro", ""),
            ("custom", "Custom Model...", ""),
        ],
        default="gemini-2.5-pro"
    )

    use_paid_tier: bpy.props.BoolProperty(name="Paid API Mode", default=False)
    custom_api_key: bpy.props.StringProperty(name="API Key", subtype='PASSWORD')
    custom_model_name: bpy.props.StringProperty(name="Model ID", default="gemini-2.0-pro-exp")
    
    ctx_scene: bpy.props.BoolProperty(name="Scene Data", default=True)
    ctx_object: bpy.props.BoolProperty(name="Active Object", default=True)
    ctx_modifiers: bpy.props.BoolProperty(name="Modifiers", default=False)
    ctx_materials: bpy.props.BoolProperty(name="Materials", default=False)

    is_primed: bpy.props.BoolProperty(name="Is Primed", default=False)
    user_input: bpy.props.StringProperty(name="", description="Type your message here")
    chat_history: bpy.props.CollectionProperty(type=GEMINI_STR_Message)

# --- Operators ---

class GEMINI_OT_WarmStart(bpy.types.Operator):
    """Silent handshake with AI to initialize the session"""
    bl_idname = "gemini.warm_start"
    bl_label = "Initialize Assistant"
    bl_description = "Establish a connection with Gemini and prime the AI context"

    def execute(self, context):
        props = context.scene.gemini_tool
        api_key = props.custom_api_key.strip() if props.use_paid_tier else DEFAULT_API_KEY.strip()
        model_id = (props.custom_model_name.strip() if props.paid_model_enum == "custom" else props.paid_model_enum) if props.use_paid_tier else props.free_model_enum

        if not api_key or api_key == "ENTER_YOUR_API_KEY_HERE":
            self.report({'ERROR'}, "Missing API Key!")
            return {'CANCELLED'}

        warm_msg = "The assistant has just been initialized inside Blender. No user question yet. Acknowledge silently."
        # Use v1beta for system_instruction support
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
        
        data = {
            "contents": [{"role": "user", "parts": [{"text": warm_msg}]}],
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]}
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), method='POST')
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=15) as response:
                props.is_primed = True
                self.report({'INFO'}, "Gemini AI initialized and ready.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to initialize: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

class GEMINI_OT_SendMessage(bpy.types.Operator):
    bl_idname = "gemini.send_message"
    bl_label = "SEND"
    bl_description = "Send message with scene context"

    def execute(self, context):
        props = context.scene.gemini_tool
        api_key = props.custom_api_key.strip() if props.use_paid_tier else DEFAULT_API_KEY.strip()
        model_id = (props.custom_model_name.strip() if props.paid_model_enum == "custom" else props.paid_model_enum) if props.use_paid_tier else props.free_model_enum

        user_text = props.user_input.strip()
        if not user_text: return {'CANCELLED'}

        context_data = get_blender_context_info(context, props)
        full_prompt = f"{context_data}\n\nUser Question: {user_text}"

        payload_contents = []
        for m in props.chat_history:
            payload_contents.append({"role": m.role, "parts": [{"text": m.content}]})
        
        payload_contents.append({"role": "user", "parts": [{"text": full_prompt}]})
        
        msg = props.chat_history.add()
        msg.role = "user"
        msg.content = user_text
        props.user_input = ""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
        data = {
            "contents": payload_contents,
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]}
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), method='POST')
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=30) as response:
                res_json = json.loads(response.read())
                answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
                reply = props.chat_history.add()
                reply.role = "model"
                reply.content = answer
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")

        context.area.tag_redraw()
        return {'FINISHED'}

class GEMINI_OT_ResetContext(bpy.types.Operator):
    bl_idname = "gemini.reset_context"
    bl_label = ""
    bl_description = "Disable all context awareness"
    def execute(self, context):
        props = context.scene.gemini_tool
        props.ctx_scene = props.ctx_object = props.ctx_modifiers = props.ctx_materials = False
        return {'FINISHED'}

class GEMINI_OT_ClearChat(bpy.types.Operator):
    bl_idname = "gemini.clear_chat"
    bl_label = "Clear History"
    def execute(self, context):
        context.scene.gemini_tool.chat_history.clear()
        return {'FINISHED'}

# --- UI Panel ---
class GEMINI_PT_Panel(bpy.types.Panel):
    bl_label = "Gemini AI Chat"
    bl_idname = "GEMINI_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Gemini AI'

    def draw(self, context):
        layout = self.layout
        props = context.scene.gemini_tool

        # 1. API Settings
        box = layout.box()
        box.prop(props, "use_paid_tier", text="Paid API Mode", icon='SETTINGS')
        if props.use_paid_tier:
            box.prop(props, "custom_api_key")
            box.prop(props, "paid_model_enum", text="")
        else:
            box.prop(props, "free_model_enum", text="")

        layout.separator()

        # 2. Warm Start / Chat Interface
        if not props.is_primed:
            welcome = layout.box()
            welcome.label(text="Assistant needs initialization", icon='INFO')
            row = welcome.row()
            row.scale_y = 1.5
            # Fix: Using 'PLAY' instead of 'POWER' for 4.3 compatibility
            row.operator("gemini.warm_start", icon='PLAY', text="Wake Up Gemini")
        else:
            # AI Awareness
            ctx_box = layout.box()
            header = ctx_box.row()
            header.label(text="AI Awareness:", icon='INFO')
            header.operator("gemini.reset_context", icon='X', emboss=False)
            
            grid = ctx_box.grid_flow(columns=2, align=True, even_columns=True)
            grid.prop(props, "ctx_scene")
            grid.prop(props, "ctx_object")
            grid.prop(props, "ctx_modifiers")
            grid.prop(props, "ctx_materials")

            layout.separator()

            # Input
            input_box = layout.box()
            input_box.prop(props, "user_input", text="", icon='URL') # 'URL' is safe in 4.3
            row = input_box.row(align=True)
            row.scale_y = 1.5
            row.operator("gemini.send_message", icon='PLAY')
            row.operator("gemini.clear_chat", icon='TRASH', text="")

            layout.separator()

            # Chat History
            if len(props.chat_history) == 0:
                layout.label(text="No messages yet...", icon='INFO')
            
            for msg in reversed(props.chat_history):
                is_user = msg.role == "user"
                row = layout.row()
                m_box = row.box()
                m_box.label(text="You" if is_user else "Gemini", icon='USER' if is_user else 'LIGHT')
                
                wrapper = textwrap.TextWrapper(width=42)
                for line in msg.content.split('\n'):
                    if not line.strip():
                        m_box.label(text="")
                        continue
                    for w_line in wrapper.wrap(text=line):
                        m_box.label(text=w_line)
                layout.separator(factor=0.5)

# --- Registration ---
classes = (
    GEMINI_STR_Message, GEMINI_STR_Settings, 
    GEMINI_OT_WarmStart, GEMINI_OT_SendMessage, 
    GEMINI_OT_ResetContext, GEMINI_OT_ClearChat, 
    GEMINI_PT_Panel
)

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.gemini_tool = bpy.props.PointerProperty(type=GEMINI_STR_Settings)

def unregister():
    for cls in reversed(classes): bpy.utils.unregister_class(cls)
    del bpy.types.Scene.gemini_tool

if __name__ == "__main__":
    register()
