from dataclasses import dataclass
import requests


@dataclass
class GenericClient:
    trello_key: str
    trello_token: str

    # definisanje get metode
    def get(self, url_endpoint: str) -> dict:
        url = "https://api.trello.com/1/" + url_endpoint

        headers = {
            "Accept": "application/json"
        }

        query = {
         'key': self.trello_key,
         'token': self.trello_token
        }

        response = requests.request(
            "GET",
            url,
            headers=headers,
            params=query
        )

        return response.json()

    # definisanje post metode
    def post(self, url_endpoint: str) -> dict:
        url = "https://api.trello.com/1/" + url_endpoint

        headers = {
            "Accept": "application/json"
        }

        query = {
            'key': self.trello_key,
            'token': self.trello_token
        }

        response = requests.request(
            "POST",
            url,
            headers=headers,
            params=query
        )
        return response.json()
