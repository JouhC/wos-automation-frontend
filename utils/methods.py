import requests
from time import time

class GiftCodeRedemptionAPI:
    def __init__(self, base_url):
        self.base_url = base_url

    def _handle_response(self, response):
        if response.status_code == 200:
            return response.json()
        
        response.raise_for_status()

    # Root endpoint
    def get_root(self):
        url = f"{self.base_url}/"
        response = requests.get(url)
        return self._handle_response(response)

    # Players endpoints
    def list_players(self):
        url = f"{self.base_url}/players/list/"
        response = requests.get(url)
        return self._handle_response(response)

    def create_player(self, player_id):
        url = f"{self.base_url}/players/create/"
        data = {"player_id": player_id}
        response = requests.post(url, json=data)
        return self._handle_response(response)
    
    def update_player_profile(self, player_id):
        url = f"{self.base_url}/players/update/"
        data = {"player_id": player_id}
        response = requests.post(url, json=data)
        return self._handle_response(response)

    # Giftcodes endpoints
    def fetch_giftcodes(self):
        url = f"{self.base_url}/giftcodes/fetch/"
        response = requests.get(url)
        return self._handle_response(response)

    def list_giftcodes(self):
        url = f"{self.base_url}/giftcodes/"
        response = requests.get(url)
        return self._handle_response(response)

    def set_giftcode_inactive(self, code):
        url = f"{self.base_url}/giftcodes/deactivate/"
        data = {"code": code}
        response = requests.post(url, json=data)
        return self._handle_response(response)

    # Redeem giftcodes endpoint
    def redeem_giftcode(self, player_id):
        url = f"{self.base_url}/redeem/"
        data = {"player_id": player_id}
        response = requests.post(url, json=data)
        return self._handle_response(response)

    # Redemptions endpoint
    def list_redeemed_codes(self, player_id):
        url = f"{self.base_url}/redemptions/{player_id}/"
        response = requests.get(url)
        return self._handle_response(response)

    # Automate-all endpoint
    def run_main_logic(self):
        url = f"{self.base_url}/automate-all/"
        response = requests.post(url)
        return self._handle_response(response)
    
    # Update Subscribed Players endpoint
    def update_players(self):
        url = f"{self.base_url}/update-players/"
        response = requests.post(url)
        return self._handle_response(response)
    
    def expired_check(self):
        url = f"{self.base_url}/giftcodes/expired-check/"
        response = requests.post(url)
        return self._handle_response(response)
    
    def get_task_status(self, task_id):
        url = f"{self.base_url}/task_status/{task_id}/"
        response = requests.get(url)
        return self._handle_response(response)

if __name__ == "__main__":
    pass
