import requests


# create base url
base_url = 'https://gmibank.netlify.app/.netlify'

user_id = 3

# First create the url

url = f'{base_url}/functions/registrants/{user_id}'


# Create the new version of the data
data = {
		     
		    "firstName": "Warren",                       
		    "lastName": "Case",                       
		    "login": "warren",                   
		    "mobilePhoneNumber": "+4044444444",         
		    "password": "Passw0rd123!",                  
		    "ssn": "333-45-8888"                       
		                                 
		}



# create the headers / content type for body data type(json, xml), authentication

header = {  'Content-Type': 'application/json'  }


# send the Put request

response  = requests.put(url, json=data, headers=header )


# validate data created
assert response.status_code in [200, 201]

print(response.status_code)

print(response.json())
