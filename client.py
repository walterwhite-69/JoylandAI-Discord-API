import httpx
import hashlib
import json
import secrets
import random

class JoylandClient:
    def __init__(self):
        self.base_url = "https://api.joyland.ai"
        self.fingerprint = secrets.token_hex(16)
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        self.user_agent = random.choice(user_agents)
        
        self.client = httpx.AsyncClient(headers={
            "accept": "application/json, text/plain, */*",
            "accept-language": "en",
            "fingerprint": self.fingerprint,
            "origin": "https://www.joyland.ai",
            "referer": "https://www.joyland.ai/",
            "source-platform": "JL-PC",
            "timezone": "GMT+6",
            "user-agent": self.user_agent,
            "authtoken": ""
        }, timeout=30.0)
        self.token = None
        self.user_ids = []

    async def login(self, email, password):
        md5_password = hashlib.md5(password.encode()).hexdigest()
        payload = {
            "email": email,
            "userPwd": md5_password,
            "srcType": "LOCAL",
            "sourceWebsite": "https://www.joyland.ai/"
        }
        
        response = await self.client.post(f"{self.base_url}/user/login", json=payload)
        data = response.json()
        
        if data.get("code") == "0":
            result = data.get("result", {})
            self.token = result.get("token")
            self.user_ids = result.get("ids", [])
            
            if self.token:
                self.client.headers["authtoken"] = self.token
                return True, data
            else:
                return False, data
        return False, data

    async def search(self, keyword, page=1, size=20):
        url = f"{self.base_url}/search/bots"
        payload = {
            "keyword": keyword,
            "page": page,
            "size": size,
            "gender": None,
            "isOnlyFeatured": False
        }
        response = await self.client.post(url, json=payload)
        return response.json()

    async def enter_dialogue(self, bot_id):
        payload = {
            "bodId": bot_id,
            "entrance": 0
        }
        response = await self.client.post(f"{self.base_url}/v1/chat/enterDialogueV2", json=payload)
        return response.json()

    async def get_chat_history(self, dialogue_id, limit=15, last_id=None):
        payload = {
            "dialogueId": dialogue_id,
            "limit": limit,
            "lastId": last_id
        }
        response = await self.client.post(f"{self.base_url}/v1/chat/chatHistory", json=payload)
        return response.json()

    async def send_message(self, dialogue_id, text_msg):
        payload = {
            "dialogueId": dialogue_id,
            "textMsg": text_msg,
            "wantImageIntention": False
        }
        
        full_response = ""
        async with self.client.stream("POST", f"{self.base_url}/v1/chat/streamChat", json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    line_data = line[5:].strip()
                    try:
                        json_data = json.loads(line_data)
                        content = json_data.get("result", {}).get("content", "")
                        if content:
                            full_response = content 
                    except:
                        pass
        return full_response

    async def close(self):
        await self.client.aclose()
