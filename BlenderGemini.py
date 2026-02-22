import bpy
import urllib.request
import urllib.error
import textwrap
import json

bl_info = {
    "name": "Blender Gemini",
    "author": "https://github.com/VittorioCodes", # Buraya GitHub kullanıcı adınızı veya isminizi yazabilirsiniz
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Gemini AI",
    "description": "Built-in API supported Gemini AI integration for Blender",
    "category": "Interface",
}

# ==========================================
# API SETTING FOR GITHUB & PERSONAL USE
# For personal use, enter your own API key here.
# When uploading to Github, leave this as "ENTER_YOUR_API_KEY_HERE".
# ==========================================
DEFAULT_API_KEY = "ENTER_YOUR_API_KEY_HERE"


# --- Data Structures ---
class GeminiMessage(bpy.types.PropertyGroup):
    role: bpy.props.StringProperty()
    content: bpy.props.StringProperty()

class GeminiSettings(bpy.types.PropertyGroup):
    # FREE MODELS (Dropdown)
    free_model_enum: bpy.props.EnumProperty(
        name="Free Model",
        description="Models suitable for Free Tier API limits",
        items=[
            ("gemini-2.5-flash", "Gemini 2.5 Flash", "Most balanced and updated free model"),
            ("gemini-2.5-flash-lite", "Gemini 2.5 Flash Lite", "Faster and lightweight model"),
            ("gemini-1.5-flash", "Gemini 1.5 Flash", "Previous generation fast model"),
        ],
        default="gemini-2.5-flash"
    )

    # PAID (PRO) MODELS (Dropdown)
    paid_model_enum: bpy.props.EnumProperty(
        name="Pro Model",
        description="Pro models for billed API keys",
        items=[
            ("gemini-2.5-pro", "Gemini 2.5 Pro", "Most advanced reasoning model"),
            ("gemini-1.5-pro", "Gemini 1.5 Pro", "Previous generation pro model"),
            ("custom", "Custom Model...", "Manually enter a new model not in the list"),
        ],
        default="gemini-2.5-pro"
    )

    use_paid_tier: bpy.props.BoolProperty(
        name="Use Paid (Pro) API",
        description="Check this if you are using a billed API key and a Pro model",
        default=False
    )

    custom_api_key: bpy.props.StringProperty(
        name="Pro API Key", 
        subtype='PASSWORD',
        description="Your API key for paid models"
    )
    
    custom_model_name: bpy.props.StringProperty(
        name="Custom Model ID", 
        default="gemini-2.0-pro-exp",
        description="e.g., gemini-2.0-pro-exp"
    )

    user_input: bpy.props.StringProperty(name="", description="Type your message...")
    chat_history: bpy.props.CollectionProperty(type=GeminiMessage)

# --- The Logic ---
class GEMINI_OT_SendMessage(bpy.types.Operator):
    bl_idname = "gemini.send_message"
    bl_label = "Send"

    def execute(self, context):
        props = context.scene.gemini_tool
        
        # Determine API Key and Model ID based on the selected mode
        if props.use_paid_tier:
            api_key = props.custom_api_key.strip()
            model_id = props.custom_model_name.strip() if props.paid_model_enum == "custom" else props.paid_model_enum
        else:
            api_key = DEFAULT_API_KEY.strip()
            model_id = props.free_model_enum

        # API Key Validation
        if not api_key or api_key == "ENTER_YOUR_API_KEY_HERE":
            self.report({'ERROR'}, "Valid API Key not found! Please edit the script or enter a key in Pro mode.")
            return {'CANCELLED'}

        user_text = props.user_input.strip()
        if not user_text:
            return {'CANCELLED'}

        # Gather chat history
        payload_contents = []
        for m in props.chat_history:
            payload_contents.append({
                "role": m.role,
                "parts": [{"text": m.content}]
            })
            
        # Overwrite if the last request failed (last message is 'user'), otherwise append
        if payload_contents and payload_contents[-1]["role"] == "user":
            payload_contents[-1] = {"role": "user", "parts": [{"text": user_text}]}
        else:
            payload_contents.append({"role": "user", "parts": [{"text": user_text}]})

        # API Configuration
        url = f"https://generativelanguage.googleapis.com/v1/models/{model_id}:generateContent?key={api_key}"
        data = {"contents": payload_contents}
        data_bytes = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(url, data=data_bytes, method='POST')
        req.add_header('Content-Type', 'application/json')

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = response.read()
                res_json = json.loads(res_data)

                if "candidates" in res_json:
                    answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    
                    if len(props.chat_history) == 0 or props.chat_history[-1].role != "user":
                        user_msg = props.chat_history.add()
                        user_msg.role = "user"
                        user_msg.content = user_text
                    else:
                        props.chat_history[-1].content = user_text
                    
                    reply = props.chat_history.add()
                    reply.role = "model"
                    reply.content = answer
                    
                    props.user_input = ""
                else:
                    self.report({'ERROR'}, "Unexpected format in API response.")
                    
        except urllib.error.HTTPError as e:
            error_response = e.read().decode('utf-8')
            try:
                err_json = json.loads(error_response)
                error_msg = err_json.get('error', {}).get('message', 'Unknown Error')
            except:
                error_msg = str(e)
            
            if "quota" in error_msg.lower() or "limit: 0" in error_response:
                self.report({'ERROR'}, f"QUOTA ERROR: Model ({model_id}) might be restricted or limit exceeded.")
            else:
                self.report({'ERROR'}, f"API Error: {error_msg}")
            print(f"DEBUG ERROR: {error_response}")

        except Exception as e:
            self.report({'ERROR'}, f"Connection Error: {str(e)}")

        context.area.tag_redraw()
        return {'FINISHED'}

class GEMINI_OT_ClearChat(bpy.types.Operator):
    bl_idname = "gemini.clear_chat"
    bl_label = "Clear"
    def execute(self, context):
        context.scene.gemini_tool.chat_history.clear()
        context.scene.gemini_tool.user_input = ""
        return {'FINISHED'}

# --- UI Layout ---
class GEMINI_PT_Panel(bpy.types.Panel):
    bl_label = "Gemini AI Chat"
    bl_idname = "GEMINI_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Gemini AI'

    def draw(self, context):
        layout = self.layout
        props = context.scene.gemini_tool

        # Settings Section
        box = layout.box()
        
        # Mode Switcher (Free vs Pro)
        box.prop(props, "use_paid_tier", icon='PMARKER_SEL')
        
        if props.use_paid_tier:
            # PAID USER INTERFACE
            box.label(text="Pro API Settings", icon='KEYINGSET')
            box.prop(props, "custom_api_key")
            box.prop(props, "paid_model_enum")
            
            # Show text box if "Custom Model" is selected
            if props.paid_model_enum == "custom":
                box.prop(props, "custom_model_name")
        else:
            # FREE USER INTERFACE (Embedded API)
            box.label(text="Embedded API Key Active", icon='LOCKED')
            box.prop(props, "free_model_enum")
        
        layout.separator()

        # Chat Area
        chat_flow = layout.box()
        if len(props.chat_history) == 0:
            chat_flow.label(text="Chat is empty...")
        
        for msg in props.chat_history:
            is_user = msg.role == "user"
            msg_box = chat_flow.box()
            msg_box.label(text="You:" if is_user else "Gemini:", icon='USER' if is_user else 'LIGHT')
            
            col = msg_box.column(align=True)
            wrapper = textwrap.TextWrapper(width=45)
            for line in msg.content.split('\n'):
                if not line.strip():
                    col.label(text="")
                    continue
                for w_line in wrapper.wrap(text=line):
                    col.label(text=w_line)

        # Bottom Input Area
        layout.separator()
        layout.prop(props, "user_input", text="")
        
        row = layout.row()
        row.scale_y = 1.5
        row.operator("gemini.send_message", icon='PLAY', text="SEND")
        layout.operator("gemini.clear_chat", icon='TRASH', text="Clear Chat")

# --- Registration ---
classes = (GeminiMessage, GeminiSettings, GEMINI_OT_SendMessage, GEMINI_OT_ClearChat, GEMINI_PT_Panel)

def register():
    for cls in classes: 
        bpy.utils.register_class(cls)
    bpy.types.Scene.gemini_tool = bpy.props.PointerProperty(type=GeminiSettings)

def unregister():
    for cls in reversed(classes): 
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.gemini_tool

if __name__ == "__main__":
    register()