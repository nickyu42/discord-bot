import requests
import json


def post_discord(username: str, content: str, url: str) -> requests.Response:
        """Post content to discord wekbook"""
        data = {'username': username, 'content': content}
        return requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data))
