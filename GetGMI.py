import requests



# Prepare request type GET

url = 'https://gmibank.netlify.app/.netlify/functions/registrants'


# step 2 : Send the request and get the response

response  = requests.get(url)

print(response.status_code)


# setp 3 we did assersion to make sure request is successful
assert response.status_code in [200, 201]

print(response.json())
