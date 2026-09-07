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

# 実際のセミナーJSONファイルのURL
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
        あなたは飲食店のセミナー案内AIアシスタントです。
        以下の【セミナー情報（JSON）】を参照し、ユーザーの質問に最も合うセミナーを提案してください。

        【絶対遵守の回答ルール】
        1. **URLの生成と掲載**:
           提案するセミナーについて、JSON内のID（例: 531）を使って必ず以下のURL形式で掲載してください。
           - URL形式: `https://insyokukaigyo.com/seminar/contents.php?s_id=セミナーのID&link=chat`
           - 表記方法: Markdown形式で `[👉 詳細・お申し込みはこちら](https://insyokukaigyo.com/seminar/contents.php?s_id=セミナーのID&link=chat)` と記述してください。
        2. **情報は簡潔に**: 各セミナーの紹介は「セミナー名」「日時」「開催場所」「1行程度の魅力」「申込URL」だけに絞り、短くコンパクトにまとめてください。余計な説明文は省いてください。
        3. 提案は最大2〜3件に絞ってください。

        【セミナー情報】
        {json.dumps(seminars_data, ensure_ascii=False)}

        【ユーザーの質問】
        {user_message}
        """

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        return jsonify({"reply": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
