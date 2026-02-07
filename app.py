from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma3:1b"

# 🧠 Chat memory
conversation = [
    {
        "role": "system",
        "content": (
            "You are a helpful AI tutor like ChatGPT. "
            "Explain answers clearly, line by line, using points and examples. "
            "If the user asks about a topic, continue explaining the SAME topic "
            "until the user explicitly says 'stop'."
        )
    }
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global conversation
    user_msg = request.json.get("message").strip()

    # 🛑 Stop command
    if user_msg.lower() == "stop":
        conversation = conversation[:1]  # keep only system message
        return jsonify({"reply": "✅ Topic stopped. Ask a new topic."})

    conversation.append({"role": "user", "content": user_msg})

    payload = {
        "model": MODEL,
        "messages": conversation,
        "stream": False
    }

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=120)
        r.raise_for_status()

        reply = r.json()["message"]["content"]
        conversation.append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"❌ Error: {str(e)}"})

if __name__ == "__main__":
     port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

