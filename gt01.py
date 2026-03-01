
import requests


def get_token():
    url = "https://talentifylabhealth.onrender.com/api/auth/login"

    credentials = {
        "username": "admin1",
        "password": "Admin123"
    }

    resp = requests.post(url, json=credentials)
    return resp.json()['token']












url2 = 'https://talentifylabhealth.onrender.com/api/orders'

baslik = {
        "Authorization": f"Bearer {get_token()}"
    }

response2  = requests.get(url2, headers=baslik)

print(response2.status_code)




url3 = 'https://talentifylabhealth.onrender.com/api/patients'

baslik2 = {
        "Authorization": f"Bearer {get_token()}"
    }

response3  = requests.get(url3, headers=baslik2)

print(response3.status_code)










# def generate_token():
#     url = "https://talentifylabhealth.onrender.com/api/auth/login"
#     credentials = {
#         "username": "admin1",
#         "password": "Admin123"
#     }
#     resp = requests.post(url, json=credentials)

#     return resp.json()['token']



# print(generate_token())
