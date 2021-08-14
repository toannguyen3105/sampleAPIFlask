import requests
api_url_telegram = "https://api.telegram.org/bot180149706233:AAEh43RlWMwZlzIf0yO2mPnJUAEkjWzmslTAE2/sendMessage?chat_id=@__groupid__&text=2"
group_id = "empire24h_telegram_bot"

def send_message_telegram(message):
    final_telegram_url = api_url_telegram.replace("__groupid__", group_id)
    final_telegram_url = final_telegram_url + message
    response = requests.get(final_telegram_url)
