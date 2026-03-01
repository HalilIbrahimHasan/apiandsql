
import requests




def get_token():

    # action 1 url set the url
    url = "https://talentifylabhealth-2edp.onrender.com/api/auth/login"



    # body required
    body = {
        "username" : "admin1",
        "password" : "Admin123"

    }


    # send the request
    response  = requests.post(url, json=body)
    return response.json()['token']



# print(get_token())













# Request 2 yapiyoruz orders

# set the url / endpoint
url_order = "https://talentifylabhealth-2edp.onrender.com/api/orders"

header = {
    "Authorization" : f"Bearer {get_token()}"
}

# send the GET request 
response = requests.get(url_order, headers=header)

# print(response.status_code)
# print(response.json())








# read all patient data
# set the url / endpoint

url_patients = "https://talentifylabhealth-2edp.onrender.com/api/orders"


# create  header
header_patient = {
    "Authorization" : f"Bearer {get_token()}"
}

# send the GET reqest

response_patients = requests.get(url_patients, headers=header_patient)

print(response_patients.status_code)
print(response_patients.json())
