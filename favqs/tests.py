import requests


url = "https://favqs.com/api/qotd"

response = requests.get(url)

print(response.status_code)
print(response.json())
