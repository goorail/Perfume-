import requests
import threading
from django.conf import settings

def send_telegram_notification(message):
    """
    Sends a message to the admin's Telegram chat.
    Runs in a background thread to prevent blocking the main Django response.
    """
    def _send():
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        chat_id = getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', None)
        
        if not token or not chat_id:
            return  # Fail gracefully if not configured locally
            
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        try:
            # 5-second timeout so the background thread doesn't hang forever
            requests.post(url, json=payload, timeout=5) 
        except Exception as e:
            print(f"Telegram notification failed: {e}")

    # Dispatch the background thread
    thread = threading.Thread(target=_send)
    thread.start()
