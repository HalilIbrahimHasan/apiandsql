import requests


url = 'https://jsonplaceholder.typicode.com/todos'


response = requests.get(url)


print(response.status_code)

print(response.json()[15])


for todo in response.json():
    
    # print(todo)  print all todos
    # print(todo['userId']) prints only the userids
    print(todo['title'])

print(type(response.json()[0]['title']))




