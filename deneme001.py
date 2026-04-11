
import requests





def get_token():
    # Set up the auth url
    auth_url = "https://talentifylabhealth.onrender.com/api/auth/login"

    headers = {
        "username": "admin1",
        "password": "Admin123"
    }

    token_response = requests.post(auth_url, json=headers)

    print(token_response.status_code)

    print(token_response.json()['token'])

    return token_response.json()['token']




def fetch_orders():
    # set the url / endpoint base url + path params + query param

    url = "https://talentifylabhealth.onrender.com/api/orders"

    headers_token = {
        "Authorization": f"Bearer {get_token()}"
    }

    response = requests.get(url, headers=headers_token)

    print(response.status_code)

    print(response.json())



fetch_orders()



