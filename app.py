from flask import Flask, render_template, request, jsonify, abort
from dotenv import load_dotenv
import os
from groq import Groq
import uuid

# ===================== SETUP =====================
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

app = Flask(__name__)

# ===================== ONE-TIME TOKENS =====================
# token : used(True/False)
ONE_TIME_TOKENS = {}

# ===================== CHAT MEMORY =====================
chat_history = [
    {
        "role": "system",
        "content": (
            "You are a chill desi AI assistant. "
            "Never say the word 'beta'. "
            "Talk casually like bro/bhai. "
            "If the user gives up, tease once then help."
        )
    }
]

# ===================== ROUTES =====================

# 🔐 MAIN PAGE (TOKEN REQUIRED)
@app.route("/", methods=["GET"])
def index():
    token = request.args.get("token")

    # token missing or invalid
    if not token or token not in ONE_TIME_TOKENS:
        return abort(403)

    # token already used
    if ONE_TIME_TOKENS[token]:
        return abort(403)

    # mark token as used (ONE-TIME)
    ONE_TIME_TOKENS[token] = True
    return render_template("index.html")


# 🤖 CHAT API
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").lower()

    giveup_words = [
        "mujhse nahi ho",
        "mere se nahi ho",
        "nahi ho raha",
        "haar maan",
        "haar gaya",
        "give up",
        "chhod",
        "chod",
        "rehne do",
        "bas"
    ]

    if any(w in user_msg for w in giveup_words):
        return jsonify({
            "reply": (
                "Chal re noob, nahi ho raha hai kya 😤\n"
                "Koi nahi bro, bata kahan atak raha hai 💪"
            )
        })

    chat_history.append({"role": "user", "content": user_msg})

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=chat_history,
        temperature=0.6,
        max_tokens=200
    )

    reply = completion.choices[0].message.content
    reply = reply.replace("beta", "").replace("Beta", "")

    chat_history.append({"role": "assistant", "content": reply})
    return jsonify({"reply": reply})


# 🔑 GENERATE ONE-TIME TOKEN
@app.route("/generate-token", methods=["GET"])
def generate_token():
    token = str(uuid.uuid4())
    ONE_TIME_TOKENS[token] = False

    return jsonify({
        "one_time_link": f"http://localhost:5000/?token={token}"
    })


# ===================== RUN SERVER =====================
if __name__ == "__main__":
    app.run(debug=True)
