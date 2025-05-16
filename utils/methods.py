import time
import requests

class GiftCodeRedemptionAPI:
    def __init__(self, base_url, max_retries=20, retry_delay=5):
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _handle_response(self, response):
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()

    def _wait_for_service(self):
        """Wait until the service is up before making any requests."""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                print(f"Waiting for API... (Attempt {attempt + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
        print("API did not start in time.")
        return False

    def _safe_request(self, method, endpoint, data=None):
        """Ensure the service is running before making the request."""
        if not self._wait_for_service():
            raise Exception("API service is not available.")

        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")

    # Root endpoint
    def get_root(self):
        return self._safe_request("GET", "/")

    # Health endpoint
    def get_health(self):
        return self._safe_request("GET", "/health")

    # Players endpoints
    def list_players(self):
        return self._safe_request("GET", "/players/list/")

    def create_player(self, player_id):
        return self._safe_request("POST", "/players/create/", {"player_id": player_id})

    def update_player_profile(self, player_id):
        return self._safe_request("POST", "/players/update/", {"player_id": player_id})
    
    def remove_player(self, player_id):
        return self._safe_request("POST", "/players/remove/", {"player_id": player_id})

    # Giftcodes endpoints
    def fetch_giftcodes(self):
        return self._safe_request("GET", "/giftcodes/fetch/")

    def list_giftcodes(self):
        return self._safe_request("GET", "/giftcodes/")

    def set_giftcode_inactive(self, code):
        return self._safe_request("POST", "/giftcodes/deactivate/", {"code": code})

    # Redeem giftcodes endpoint
    def redeem_giftcode(self, player_id):
        return self._safe_request("POST", "/redeem/", {"player_id": player_id})

    # Redemptions endpoint
    def list_redeemed_codes(self, player_id):
        return self._safe_request("GET", f"/redemptions/{player_id}/")

    # Automate-all endpoint
    def run_main_logic(self):
        return self._safe_request("POST", "/automate-all/", {"n": 'all'})

    # Update Subscribed Players endpoint
    def update_players(self):
        return self._safe_request("POST", "/update-players/")

    def expired_check(self):
        return self._safe_request("POST", "/giftcodes/expired-check/")

    def get_task_status(self, task_id):
        return self._safe_request("GET", f"/task_status/{task_id}/")

    def get_check_inprogress(self):
        return self._safe_request("GET", "/task_status/check_inprogress/")
