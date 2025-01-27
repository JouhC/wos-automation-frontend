import requests

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
        url = f"{self.base_url}/players/"
        response = requests.get(url)
        return self._handle_response(response)

    def create_player(self, player_id):
        url = f"{self.base_url}/players/"
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

# Example usage
if __name__ == "__main__":
    api = GiftCodeRedemptionAPI(base_url="https://example.com/api")

    # Example calls
    try:
        print(api.get_root())
        print(api.list_players())
        print(api.create_player(player_id="player123"))
        print(api.fetch_giftcodes())
        print(api.list_giftcodes())
        print(api.set_giftcode_inactive(code="GIFT123"))
        print(api.redeem_giftcode(player_id="player123"))
        print(api.list_redeemed_codes(player_id="player123"))
        print(api.run_main_logic())
        print(api.update_players())
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
