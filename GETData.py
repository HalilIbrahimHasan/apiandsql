import requests


def get_token():
    url = "http://localhost:5000/api/auth/login"

    credentials = {
        "username": "admin1",
        "password": "Admin123"
    }

    resp = requests.post(url, json=credentials)
    resp.raise_for_status()

    return resp.json()["token"]


def get_results(token):
    url = "https://talentifylabhealth.onrender.com/api/results"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    token = get_token()
    results = get_results(token)

    print(results)
