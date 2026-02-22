# 🤖 Blender Gemini AI (v1.1.0)

![Blender Version](https://img.shields.io/badge/Blender-3.0+-orange.svg)
![License](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Gemini API](https://img.shields.io/badge/API-Google_Gemini-blueviolet.svg)
![Version](https://img.shields.io/badge/Version-1.1.0-green.svg)

**Blender Gemini** is a state-aware AI assistant integrated directly into the Blender 3D Viewport. Unlike standard chat add-ons, it understands your scene's context, helping you model, script, and troubleshoot faster.

---

## ✨ New in v1.1.0: State-Awareness
Your AI assistant is no longer blind! It can now see:
- **Active Object Data:** Name, Type, and Location.
- **Geometry Stats:** Vertex and Face counts.
- **Modifier Stack:** List of active modifiers on your object.
- **Materials:** Applied materials and slots.
- **Scene Info:** Blender version, Render engine, and current Interaction Mode.

---

## 🚀 Key Features

- **Context Awareness:** Toggle what the AI knows about your scene to get specific answers like *"Why is my mesh so heavy?"* or *"Help me clean up these modifiers."*
- **Silent Handshake:** Professional "Warm Start" initialization to ensure the API is ready and the AI understands its role before you ask your first question.
- **Optimized for Scripting:** Generates valid `bpy` (Blender Python) code snippets tailored to your active object.
- **Zero Dependencies:** Uses Blender's built-in libraries. No pip, no requests, no headache.
- **Pro & Free Tier Support:** Switch between Free models (Gemini 2.5 Flash) and Pro models with custom API keys.

---

## 🛠️ How to Install

1. **Get an API Key:** Create a free key at [Google AI Studio](https://aistudio.google.com/).
2. **Download:** Get the `BlenderGemini.py` file from the [Latest Release](../../releases/latest).
3. **Configure:** Open the `.py` file in a text editor and paste your key at `DEFAULT_API_KEY = "YOUR_KEY_HERE"`.
4. **Install:** 
   - Open Blender > Edit > Preferences > Add-ons > Install.
   - Select `BlenderGemini.py`.
   - Enable **Interface: Blender Gemini AI**.

---

## 💻 Usage

1. Open the Sidebar in the 3D Viewport (**N key**).
2. Click the **Gemini AI** tab.
3. Click **"Wake Up Gemini"** to initialize the assistant.
4. **Configure Awareness:** Check the boxes (Scene, Object, etc.) to share context with the AI.
5. **Chat:** Type your question and hit **SEND**.

*Tip: Use the **X** button next to "AI Awareness" to quickly disable all context sharing for a generic chat experience.*

---

## 📜 Credits & License
Developed by **[VittorioCodes](https://github.com/VittorioCodes)**.

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**. Free to use, free to modify, open-source forever.

---
*Note: If Blender freezes for a few seconds during a request, it is waiting for the Google API response. This is expected behavior.*
