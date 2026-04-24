from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
import os

app = Flask(__name__, static_folder=".")
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

conversation_history = []

SHOP_SYSTEM = """You are an AI assistant for "Farhan's Shop," a mobile accessories store. Your role is to help customers find and buy mobile accessories by recommending products with their names, short descriptions, and prices in PKR. Always respond in a friendly, helpful shopkeeper tone and keep your answers short and easy to read. Every response must include the product name, a brief 1–2 line description, and the price in PKR. When a user asks for recommendations, suggest 2 to 4 options. If the user provides a budget, only show products within that range. If they ask for "cheap," focus on budget-friendly items, and if they ask for "best," suggest premium options. If the user's request is unclear, ask a simple follow-up question. You can recommend products from categories such as earbuds or headphones, chargers (including fast and wireless), mobile covers or cases, power banks, screen protectors, data cables, and mobile stands or holders. Always format your responses as a clean, numbered list showing product name, description, and price, and avoid long paragraphs or unnecessary technical jargon unless the user specifically asks for it."""

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/api/health")
def health():
    return jsonify({"status": "running"})

@app.route("/api/clear", methods=["POST"])
def clear_chat():
    global conversation_history
    conversation_history = []
    return jsonify({"message": "cleared"})

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"error": "Empty message"}), 400

        conversation_history.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SHOP_SYSTEM},
                *conversation_history
            ],
            max_tokens=500
        )

        reply = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": reply})

        return jsonify({"response": reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
