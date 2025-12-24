from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import os
from groq import Groq

app = Flask(__name__)
CORS(app)  # Allows your Google Site to talk to this server

# Initialize Groq Client
# Tip: It's safer to use an environment variable for your key!
client = Groq(api_key="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")

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
            model="llama3-8b-8192",
        )
        csharp_code = chat_completion.choices[0].message.content
    except Exception as e:
        return jsonify({"error": f"AI Error: {str(e)}"}), 500

    # 2. Save the AI code to a temporary file
    with open("Mod.cs", "w") as f:
        f.write(csharp_code)

    # 3. Compile the .cs file into a .dll
    # This command uses 'mcs' (Mono) to link your uploaded Gorilla Tag DLLs
    try:
        subprocess.run([
            "mcs", 
            "-target:library", 
            "-r:UnityEngine.dll,UnityEngine.CoreModule.dll,BepInEx.dll,Utilla.dll", 
            "-out:GTMaker_Mod.dll", 
            "Mod.cs"
        ], check=True)
        
        # 4. Send the finished .dll file back to the website user
        return send_file("GTMaker_Mod.dll", as_attachment=True)

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Compilation failed. The AI might have written buggy code."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Koyeb and other hosts usually look for port 8000 or 8080
    app.run(host='0.0.0.0', port=8000)
