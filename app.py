from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

# 在这里填入你的 DeepSeek API Key
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '') 
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    course_context = data.get('context', '')   # 新增：接收课程上下文
    
    if not user_message:
        return jsonify({"reply": "请发送有效的问题。"})
    
    # 构建系统提示词
    system_prompt = "你是一个学习助教，帮助用户解答编程、设计、数据分析等问题。"
    if course_context:
        system_prompt += f"\n\n当前课程的内容介绍如下：{course_context}\n\n请基于上述课程内容回答用户的问题。如果用户要求总结，请根据课程内容进行总结。"
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "stream": False
    }
    try:
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
    except Exception as e:
        print("错误:", e)
        return jsonify({"reply": "抱歉，AI 服务暂时不可用，请稍后再试。"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)