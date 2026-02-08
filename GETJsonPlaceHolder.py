
import requests


response = requests.get('https://jsonplaceholder.typicode.com/todos/5')

print(response.status_code)

print(response.json())








