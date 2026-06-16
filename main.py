import os
import requests
import time

def send_message(text):
    TOKEN = os.getenv("BOT_TOKEN")
    # هذا الرابط يرسل رسالة مباشرة لتليجرام لتجربة الاتصال
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    print("جاري اختبار الاتصال...")
    send_message("Test")
    # إبقاء السيرفر نشطاً
    while True:
        time.sleep(60)
