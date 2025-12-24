from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import os
import re
from groq import Groq

app = Flask(__name__)
CORS(app)

# Important: Make sure your Groq API Key is pasted here!
client = Groq(api_key="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")

def clean_code(raw_code):
    # This specifically fixes the "CS1056: Unexpected character" error from your 2nd image
    clean = re.sub(r'```[a-zA-Z]*', '', raw_code)
    clean = clean.replace('```', '')
    return clean.strip()

@app.route('/generate-mod', methods=['POST'])
def generate_mod():
    data = request.json
    user_prompt = data.get('prompt')

    try:
        # Using the updated model to fix the "Decommissioned" error from your 1st image
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": """You are a Gorilla Tag Mod developer. 
                    - Write ONLY C# code for BepInEx. 
                    - DO NOT use markdown code blocks or backticks.
                    - DO NOT use 'UnityEngine.InputSystem'. Use standard 'UnityEngine.Input'.
                    - Start code immediately with 'using' statements."""
                },
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
        )
        csharp_code = clean_code(chat_completion.choices[0].message.content)
    except Exception as e:
        return jsonify({"error": f"AI Error: {str(e)}"}), 500

    with open("Mod.cs", "w") as f:
        f.write(csharp_code)

    try:
        # We add mscorlib.dll to fix the 'System.Object' error seen in your last 3 images
        compile_process = subprocess.run([
            "mcs", "-target:library", 
            "-r:mscorlib.dll,UnityEngine.dll,UnityEngine.CoreModule.dll,UnityEngine.InputModule.dll,BepInEx.dll,Utilla.dll", 
            "-out:GTMaker_Mod.dll", "Mod.cs"
        ], capture_output=True, text=True)
        
        if compile_process.returncode != 0:
            return jsonify({"error": compile_process.stderr, "code": csharp_code}), 500
            
        return send_file("GTMaker_Mod.dll", as_attachment=True)

    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
