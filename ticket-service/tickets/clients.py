import requests

import os 

BASE_URL = os.getenv("AUTH_SERVICE_URL")


class AuthServiceUnavailable(Exception):
    pass

class AuthClient:

    @staticmethod
    def get_user(user_id,access_token):
        try:
            response = requests.get(
                f"{BASE_URL}/api/profile/{user_id}",
                headers={
                    "Authorization":f"Bearer {access_token}"
                },
                timeout=2
            )
        except requests.exceptions.RequestException:
            raise AuthServiceUnavailable    

        return response
