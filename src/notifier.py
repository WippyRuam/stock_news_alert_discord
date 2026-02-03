import requests
import os

def send_to_discord(content):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    data = {
        "username": "Stock_news_Bot",
        "content": "**รายงานสรุปหุ้นอเมริกาประจำวัน**",
        "embeds": [{
            "description": content,
            "color": 5814783 # สีน้ำเงิน
        }]
    }
    requests.post(webhook_url, json=data)