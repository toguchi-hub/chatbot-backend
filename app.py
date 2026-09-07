import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)  # WebサイトからのAPIアクセス（CORS）を許可

# 環境変数からGEMINI_API_KEYを取得
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# セミナーJSONファイルのURL
SEMINAR_JSON_URL = "https://insyokukaigyo.com/js/seminar.json"

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "Chatbot API is running"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # 1. サイトからセミナー情報を取得
    try:
        response = requests.get(SEMINAR_JSON_URL, timeout=5)
        response.raise_for_status()
        seminars_data = response.json()
    except Exception as e:
        seminars_data = f"セミナー情報の取得に失敗しました: {str(e)}"

    # 2. Geminiへ問い合わせ
    try:
        prompt = f"""
        あなたはセミナー案内AIアシスタントです。
        以下のセミナー情報（JSON形式）を読み込み、ユーザーの質問や要望に最も適したセミナーを分かりやすく提案・説明してください。

        【セミナー情報】
        {json.dumps(seminars_data, ensure_ascii=False)}

        【ユーザーの質問】
        {user_message}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return jsonify({"reply": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
