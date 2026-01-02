from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ.get('OPENAI_API_KEY')
conversations = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    
    if from_number not in conversations:
        conversations[from_number] = [
            {"role": "system", "content": "أنت مساعد ذكي لشركة درب للاستثمار السياحي. تساعد العملاء بالإجابة على استفساراتهم بطريقة احترافية وودية باللغة العربية."}
        ]
    
    conversations[from_number].append({"role": "user", "content": incoming_msg})
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversations[from_number],
            max_tokens=500,
            temperature=0.7
        )
        bot_reply = response.choices[0].message.content
        conversations[from_number].append({"role": "assistant", "content": bot_reply})
    except Exception as e:
        bot_reply = f"عذراً، حدث خطأ: {str(e)}"
    
    resp = MessagingResponse()
    resp.message(bot_reply)
    return str(resp)

@app.route('/')
def home():
    return "✅ بوت WhatsApp يعمل بنجاح! 🚀"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

