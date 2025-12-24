from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import os
import re
from groq import Groq

app = Flask(__name__)
CORS(app)

# Use your active Groq API Key
client = Groq(api_key="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")

def clean_code(raw_code):
    # Fixes CS1056: Strips Markdown blocks that cause the 'Unexpected character' error
    clean = re.sub(r'```[a-zA-Z]*', '', raw_code)
    clean = clean.replace('```', '')
    return clean.strip()

@app.route('/generate-mod', methods=['POST'])
def generate_mod():
    data = request.json
    user_prompt = data.get('prompt')

    try:
        # Use the updated model llama-3.3-70b-versatile
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": """Write ONLY C# code for a Gorilla Tag BepInEx mod. 
                    - Do NOT use Markdown code blocks or backticks.
                    - Use 'using UnityEngine;' and 'using BepInEx;'.
                    - For controller support, use standard 'UnityEngine.Input'.
                    - Ensure every class inherits from 'BaseUnityPlugin'."""
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
        # We add -r:mscorlib.dll to fix the 'System.Object' error seen in your 5th image
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

@app.route('/get-last-code', methods=['GET'])
def get_last_code():
    if os.path.exists("Mod.cs"):
        with open("Mod.cs", "r") as f:
            return jsonify({"code": f.read()})
    return jsonify({"error": "No code found"}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
