from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from huggingface_hub import InferenceClient
import os

app = Flask(__name__)

# Hugging Face API
hf_token = os.environ.get('HUGGINGFACE_API_KEY', '')
client = InferenceClient(token=hf_token)

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number_user = request.values.get('From', '')
    
    # رسالة النظام
    system_message = """أنت مساعد ذكي لشركة درب للاستثمار السياحي في ليبيا.
مهمتك مساعدة العملاء بالإجابة على أسئلتهم حول:
- استخراج تأشيرات شنغن
- حجوزات الطيران والفنادق
- برامج سياحية مخصصة
- استشارات سفر

أجب بشكل احترافي ومفيد باللغة العربية. اجعل ردودك قصيرة ومباشرة."""

    prompt = f"{system_message}\n\nالعميل: {incoming_msg}\n\nالمساعد:"
    
    try:
        # استخدام Hugging Face Inference API
        # نستخدم نموذج Meta Llama 3 (يدعم العربية بشكل ممتاز)
        response = client.text_generation(
            prompt,
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            max_new_tokens=300,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1
        )
        
        bot_reply = response.strip()
        
        # إذا كان الرد فارغاً
        if not bot_reply:
            bot_reply = "عذراً، لم أتمكن من الرد. يرجى إعادة المحاولة أو التواصل مع فريق الدعم."
        
        # تحديد طول الرد (WhatsApp يدعم حتى 1600 حرف)
        if len(bot_reply) > 1500:
            bot_reply = bot_reply[:1500] + "..."
            
    except Exception as e:
        error_msg = str(e)
        if "rate limit" in error_msg.lower():
            bot_reply = "عذراً، النظام مشغول حالياً. يرجى المحاولة بعد قليل."
        elif "timeout" in error_msg.lower():
            bot_reply = "عذراً، انتهت مهلة الاتصال. يرجى المحاولة مرة أخرى."
        else:
            bot_reply = f"عذراً، حدث خطأ. يرجى التواصل مع فريق الدعم."
    
    resp = MessagingResponse()
    resp.message(bot_reply)
    return str(resp)

@app.route('/')
def home():
    return "مرحباً بك في بوت درب للاستثمار السياحي! 🚀"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
