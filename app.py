from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import os
from groq import Groq

app = Flask(__name__)
CORS(app) # This allows your Google Site to talk to this server

# Initialize Groq Client
# Tip: Make sure your API Key is active at console.groq.com
client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")

@app.route('/')
def health_check():
    return "The Gorilla Tag Mod Compiler is Online!"

@app.route('/generate-mod', methods=['POST'])
def generate_mod():
    data = request.json
    user_prompt = data.get('prompt')

    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # 1. Ask the AI to write the C# code
    # We are using 'llama-3.3-70b-versatile' as the older model was retired
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "You are a Gorilla Tag Mod developer. Write only the C# code for a BepInEx mod using Utilla. No conversational text, only the code."
                },
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        csharp_code = chat_completion.choices[0].message.content
    except Exception as e:
        # This sends the "Model Decommissioned" or "API Key" error to your site
        return jsonify({"error": f"AI Error: {str(e)}"}), 500

    # 2. Save the AI code to a temporary file
    with open("Mod.cs", "w") as f:
        f.write(csharp_code)

    # 3. Compile the .cs file into a .dll
    # We capture the output so we can see why it fails (Missing DLLs, etc.)
    try:
        compile_process = subprocess.run([
            "mcs", 
            "-target:library", 
            "-r:UnityEngine.dll,UnityEngine.CoreModule.dll,BepInEx.dll,Utilla.dll", 
            "-out:GTMaker_Mod.dll", 
            "Mod.cs"
        ], capture_output=True, text=True)
        
        if compile_process.returncode != 0:
            # If the C# code is bad, send the specific error to the website
            return jsonify({"error": compile_process.stderr}), 500
            
        # 4. Send the finished .dll file back to the website user
        return send_file("GTMaker_Mod.dll", as_attachment=True)

    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

if __name__ == "__main__":
    # Koyeb uses port 8000 by default
    app.run(host='0.0.0.0', port=8000)
