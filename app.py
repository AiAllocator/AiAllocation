from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
import google.generativeai as genai
import json
import re

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__, static_folder="static")
CORS(app)

# Define the list of allowed tools
ALLOWED_TOOLS = [
    "ChatGPT", "Claude", "Gemini", "DeepSeek", "Synthesia", "Runway", "Filmora", "OpusClip",
    "Fathom", "Nyota", "Deep Research", "Rytr", "Sudowrite", "Grammarly", "Wordtune",
    "Perplexity", "ChatGPT-Suche", "Vista Social", "FeedHive", "Midjourney", "DALL·E 3",
    "Synthesia Magic Studio", "Looka", "Bubble", "Bolt", "Lovable", "Cursor", "v0",
    "Asana", "ClickUp", "Reclaim", "Clockwise", "Tidio KI", "Hiver", "Textio", "CVViZ",
    "Notion AI Q&A", "Guru", "Hubspot Email Writer", "SaneBox", "Kurzwelle", "Gamma",
    "Presentations.ai", "Teal", "Kickresume", "ElevenLabs", "Murf", "Suno", "Udio",
    "AdCreative", "Clay"
]

# Use original names with no transformation (preserve case)
def sanitize_filename(name):
    return name.replace(" ", "").replace("-", "").replace("·", "").replace(".", "") + ".png"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user_prompt = data.get("prompt", "")

    allowed_tools_list = "\n".join([f"- {tool}" for tool in ALLOWED_TOOLS])

    prompt = f"""
You are an expert AI assistant who recommends AI tools.

Your task:
Given this user request: "{user_prompt}"
→ Recommend only relevant AI tools from the approved list below.

Approved Tools:
{allowed_tools_list}

Respond ONLY with valid JSON in this format:
{{
  "category": "Category Name",
  "tools": [
    {{ "name": "Tool1", "reason": "why it's good" }},
    {{ "name": "Tool2", "reason": "why it's good" }}
  ]
}}

- Do not include tools not listed above.
- Do not include anything outside the JSON.
- Do not include comments.
- Ensure the JSON is strictly valid.
"""

    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        response = model.generate_content(prompt)

        print("\n=== Gemini RESPONSE ===\n")
        print(response.text)
        print("\n========================\n")

        try:
            # Remove markdown code block formatting if present
            cleaned = re.sub(r"```(?:json)?\s*([\s\S]*?)\s*```", r"\1", response.text.strip())
            parsed = json.loads(cleaned)

            # Add logo field based on name (preserving original casing)
            for tool in parsed.get("tools", []):
                name = tool.get("name", "")
                tool["logo"] = sanitize_filename(name)

            return jsonify(parsed)
        except Exception as e:
            return jsonify({"error": "Invalid JSON", "raw": response.text}), 500

    except Exception as e:
        print("❌ Gemini API error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/")
def serve_index():
    return send_file("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


