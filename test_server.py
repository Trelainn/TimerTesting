import requests

api_url = "https://www.sea-maze.fr/api/"

def getAccessToken():
    data = {"email": "test_user@sea-maze.fr", "password": "testing"}
    response = requests.post(api_url + "auth/login", json=data)
    print(response)
    return response.json()["access_token"]

def getUserBasicInfo():
    response = requests.get(api_url + "users/basicInfo", headers={"Authorization": "Bearer " + getAccessToken()})
    print(response.json())

getUserBasicInfo()