# 🤖 Blender Gemini

![Blender Version](https://img.shields.io/badge/Blender-3.0+-orange.svg)
![License](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Gemini API](https://img.shields.io/badge/API-Google_Gemini-blueviolet.svg)

**Blender Gemini** is a lightweight, zero-dependency Blender add-on that brings Google's powerful Gemini AI directly into your 3D viewport. 

Whether you need to ask for exact real-world dimensions (e.g., *"What is the standard height of a kitchen counter?"*), get Python (bpy) scripting help, or brainstorm modeling ideas, your AI assistant is now just a click away inside Blender!

---

## ✨ Features

- **No External Libraries Required:** Uses Blender's built-in `urllib`. No need to install `requests` or mess with Python environments. Just plug and play!
- **Free Tier Optimized:** Fully supports Google's Free Tier models. Comes with a built-in dropdown for `gemini-2.5-flash-lite` (offering generous limits like 1,000 requests/day for free users).
- **Pro & Custom Model Support:** Advanced users can toggle the "Pro Mode" to input billed API keys and use advanced reasoning models like `gemini-2.5-pro` or even type in experimental custom model IDs.
- **Smart UI:** Neatly wraps text to fit Blender's sidebar, keeps chat history intact, and handles API errors gracefully with built-in pop-up warnings.
- **Wide Compatibility:** Works seamlessly with Blender 3.0, 3.6 LTS, 4.0, and newer versions.

---

## 🛠️ Use Cases for 3D Artists
* **Real-World Scale:** Ask for exact dimensions of everyday objects to keep your scenes anatomically and proportionally correct.
* **Material & Lighting Tips:** Ask how to achieve specific PBR material looks or lighting setups.
* **Blender Python (bpy):** Quickly generate small scripts to automate repetitive tasks.

---

## 🚀 Step-by-Step Installation Guide

Even if you have never used an add-on or an API before, just follow these simple steps:

### Step 1: Get Your Free Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click on **"Get API key"** (usually on the left menu) and create a new key.
4. Copy this key. Keep it secret!

### Step 2: Download & Prepare the Add-on
1. Go to the **[Releases](../../releases/latest)** section on the right side of this GitHub repository.
2. Under the "Assets" dropdown of the latest release, click on `BlenderGemini.py` to download it directly.
3. Open the downloaded `BlenderGemini.py` file with any basic text editor (like **Notepad** on Windows or **TextEdit** on Mac).
4. Look near the top of the file for **Line 22**, which looks exactly like this:

   ```python
   DEFAULT_API_KEY = "ENTER_YOUR_API_KEY_HERE"
5. Replace ENTER_YOUR_API_KEY_HERE with the API key you copied from Google. (Make sure you keep the quotation marks "" around your key).
6. Save the file and close the text editor.

### Step 3: Install in Blender
1. Open Blender.
2. Go to **Edit > Preferences > Add-ons**.
3. Click the **Install...** button at the top right.
4. Find and select your modified `BlenderGemini.py` file and click **Install Add-on**.
5. Tick the checkbox next to **Interface: Gemini AI Chat Pro** (or Blender Gemini) to enable it.

---

## 💻 How to Use

1. Go to your **3D Viewport** in Blender.
2. Press **`N`** on your keyboard to open the right Sidebar.
3. Click on the new **Gemini AI** tab.
4. **Select a Model:** 
   * *Recommendation:* Choose **Gemini 2.5 Flash Lite** from the dropdown. It is incredibly fast and gives you a massive 1,000 requests/day for free!
5. Type your question in the text box at the bottom and click **SEND**.

*(Note: Blender's interface might freeze for a second while waiting for the AI's response. This is completely normal.)*

---

## ⚠️ Troubleshooting & FAQ

**Error: "Valid API Key not found!"**
You forgot to paste your API key into the `.py` file before installing. Disable the add-on, edit the file, save it, and reinstall.

**Error: "QUOTA ERROR / Limit Exceeded"**
Google has strict rate limits for free models. If you send messages too fast (more than 15 per minute), you will get this error. Just wait 5-10 seconds and try again. If your daily limit is completely zeroed out, make sure you are using the `gemini-2.5-flash-lite` model from the dropdown.

**Can I use Paid Models?**
Yes! Check the **"Use Paid (Pro) API"** box in the add-on settings. A new menu will appear allowing you to enter a billed API key and select advanced reasoning models.

---

## 🤝 Contributing
Feel free to fork this project, submit pull requests, or report issues in the "Issues" tab. Let's make the best AI integration for Blender together!

## 📜 License
This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)** - see the [LICENSE](LICENSE) file for details. This ensures the add-on remains free and open-source forever.
