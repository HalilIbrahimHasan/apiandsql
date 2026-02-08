
import requests


url = 'https://jsonplaceholder.typicode.com/todos'

parqueryParam = {   'title'  :   "sit reprehenderit omnis quia" }

response = requests.get(url, params=parqueryParam)


print(response.status_code)

print(response.json())
