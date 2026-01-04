from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os
import re

app = Flask(__name__)

# Clean API key from any whitespace or newlines
def clean_api_key(key):
    if key:
        return re.sub(r'\s+', '', key)
    return ''

gemini_api_key = clean_api_key(os.environ.get('GEMINI_API_KEY', ''))
twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
from_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number_user = request.values.get('From', '')
    
    prompt = f"""أنت مساعد ذكي لشركة درب للاستثمار السياحي. مهمتك مساعدة العملاء بالإجابة على أسئلتهم حول الخدمات التالية:

1. استخراج تأشيرات شنغن
2. حجوزات الطيران والفنادق
3. برامج سياحية مخصصة
4. استشارات سفر

السؤال: {incoming_msg}

الرجاء الإجابة بشكل احترافي ومفيد باللغة العربية."""
    
    try:
        # Gemini API endpoint
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}'
        
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            json={
                'contents': [{
                    'parts': [{'text': prompt}]
                }],
                'generationConfig': {
                    'temperature': 0.7,
                    'maxOutputTokens': 500
                }
            },
            timeout=10
         )
        
        result = response.json()
        
        # معالجة أفضل للرد
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                bot_reply = candidate['content']['parts'][0]['text']
            else:
                bot_reply = f"عذراً، لم أتمكن من الرد. السبب: {candidate.get('finishReason', 'غير معروف')}"
        elif 'error' in result:
            error_msg = result['error'].get('message', 'خطأ غير معروف')
            bot_reply = f"عذراً، حدث خطأ من Gemini: {error_msg}"
        else:
            bot_reply = f"عذراً، رد غير متوقع من Gemini. التفاصيل: {str(result)[:200]}"
        
    except requests.exceptions.Timeout:
        bot_reply = "عذراً، انتهت مهلة الاتصال بـ Gemini. حاول مرة أخرى."
    except requests.exceptions.RequestException as e:
        bot_reply = f"عذراً، خطأ في الاتصال: {str(e)}"
    except Exception as e:
        bot_reply = f"عذراً، حدث خطأ: {str(e)}"
    
    resp = MessagingResponse()
    resp.message(bot_reply)
    return str(resp)

@app.route('/')
def home():
    return "مرحباً بك في بوت درب للاستثمار السياحي! 🚀"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
