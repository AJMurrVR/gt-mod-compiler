from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import os
import re
from groq import Groq

app = Flask(__name__)
CORS(app)

# Initialize Groq Client
client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")

def clean_code(raw_code):
    # This removes ```csharp and ``` blocks that cause the CS1056 error
    clean = re.sub(r'```[a-zA-Z]*', '', raw_code)
    clean = clean.replace('```', '')
    return clean.strip()

@app.route('/')
def health_check():
    return "Mod Compiler is Online!"

@app.route('/generate-mod', methods=['POST'])
def generate_mod():
    data = request.json
    user_prompt = data.get('prompt')

    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        # Using the updated model
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Write ONLY the C# code for a Gorilla Tag BepInEx mod using Utilla. Do not use markdown code blocks like ```csharp. Start directly with 'using'."},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
        )
        raw_code = chat_completion.choices[0].message.content
        csharp_code = clean_code(raw_code) # Clean the code before saving
    except Exception as e:
        return jsonify({"error": f"AI Error: {str(e)}"}), 500

    # Save the cleaned code
    with open("Mod.cs", "w") as f:
        f.write(csharp_code)

    try:
        # Compile the cleaned code
        compile_process = subprocess.run([
            "mcs", "-target:library", 
            "-r:UnityEngine.dll,UnityEngine.CoreModule.dll,BepInEx.dll,Utilla.dll", 
            "-out:GTMaker_Mod.dll", "Mod.cs"
        ], capture_output=True, text=True)
        
        if compile_process.returncode != 0:
            return jsonify({"error": compile_process.stderr}), 500
            
        return send_file("GTMaker_Mod.dll", as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
