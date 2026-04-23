from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
import os

app = Flask(__name__, static_folder=".")
CORS(app)

# ── Configuration ──────────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL        = "mixtral-8x7b-32768"   # Change to any Groq-supported model
# Other options: "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"

client = Groq(api_key=GROQ_API_KEY)

# ── Routes ─────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "messages" not in data:
        return jsonify({"error": "Missing 'messages' in request body"}), 400

    messages = data["messages"]          # Full conversation history from frontend
    system_prompt = data.get(
        "system",
        "You are an AI assistant for “Farhan’s Shop,” a mobile accessories store. Your role is to help customers find and buy mobile accessories by recommending products with their names, short descriptions, and prices in PKR. Always respond in a friendly, helpful shopkeeper tone and keep your answers short and easy to read. Every response must include the product name, a brief 1–2 line description, and the price in PKR. When a user asks for recommendations, suggest 2 to 4 options. If the user provides a budget, only show products within that range. If they ask for “cheap,” focus on budget-friendly items, and if they ask for “best,” suggest premium options. If the user’s request is unclear, ask a simple follow-up question. You can recommend products from categories such as earbuds or headphones, chargers (including fast and wireless), mobile covers or cases, power banks, screen protectors, data cables, and mobile stands or holders. Always format your responses as a clean, numbered list showing product name, description, and price, and avoid long paragraphs or unnecessary technical jargon unless the user specifically asks for it."
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system_prompt}] + messages,
            max_tokens=1024,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Entry Point ────────────────────────────────────────────────
if _name_ == "_main_":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
