
import requests


# create base url
base_url = 'https://gmibank.netlify.app/.netlify'

user_id = 1769098895192

# First create the url

url = f'{base_url}/functions/registrants/{user_id}'


# Send the Delete request and get the response

response = requests.delete(url)

# assert / validate the record has been removed

assert response.status_code in [200, 204]

print(response.status_code)