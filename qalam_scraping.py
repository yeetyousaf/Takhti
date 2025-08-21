from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os

load_dotenv()

session = requests.Session()

login_url = 'https://qalam.nust.edu.pk/web/login'
response = session.get(login_url)
soup = BeautifulSoup(response.text, 'lxml')

csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

payload = {
    "csrf_token": csrf_token,
    "login": os.getenv('QALAM_USERNAME'),
    "password": os.getenv('QALAM_PASSWORD'),
}

login_response = session.post(login_url, data=payload)
print(f"Status code: {login_response.status_code}")
