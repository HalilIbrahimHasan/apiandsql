import requests



# First create the url

url = 'https://gmibank.netlify.app/.netlify/functions/registrants'


# Create the necessary data
data = {
		    "email": "ibrahim@gmail.com",         
		    "firstName": "Ibrahim",                       
		    "lastName": "Kalin",                       
		    "login": "ibrahim",                   
		    "mobilePhoneNumber": "+2022022222",         
		    "password": "Passw0rd123!",                  
		    "ssn": "263-45-6789"                       
		                                 
		}



# create the headers / content type for body data type(json, xml), authentication

header = {  'Content-Type': 'application/json'  }


# send the Post request

response  = requests.post(url, json=data, headers=header )


# validate data created
assert response.status_code == 201

print(response.status_code)
