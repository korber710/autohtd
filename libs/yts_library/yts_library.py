import requests
import difflib

class YTSController:
    def __init__(self):
        pass

    def search(self, query):
        returnObj = {
            "result": -1,
            "description": "",
            "data": ""
        }
        payload = {"query_term": query, "order_by": "asc"}
        response = requests.post('https://yts.mx/api/v2/list_movies.json', params=payload)
        if response.status_code == 200:
            returnObj["result"] = 0
            returnObj["description"] = "search successful"
            movies = []
            if "movies" in response.json()["data"]:
                for i in range(len(response.json()["data"]["movies"])):
                    movies.append(response.json()["data"]["movies"][i]["title_long"])
            else:
                returnObj["result"] = -1
                returnObj["description"] = "search:: couldn't find any movies"
                return returnObj
            try:
                bestMovie = difflib.get_close_matches(query, movies)[0]
            except:
                returnObj["result"] = -1
                returnObj["description"] = "search:: couldn't find a good match"
                return returnObj
            for i in range(len(response.json()["data"]["movies"])):
                if bestMovie == response.json()["data"]["movies"][i]["title_long"]:
                    index = i
                    break
            returnObj["data"] = response.json()["data"]["movies"][index]
            return returnObj
        else:
            returnObj["result"] = -1
            returnObj["description"] = "search:: bad response"
            return returnObj

    def search_all(self, query):
        returnObj = {
            "result": -1,
            "description": "",
            "data": ""
        }
        payload = {"query_term": query, "order_by": "asc"}
        response = requests.post('https://yts.mx/api/v2/list_movies.json', params=payload)
        if response.status_code == 200:
            returnObj["result"] = 0
            returnObj["description"] = "search successful"
            if "movies" in response.json()["data"]:
                returnObj["data"] = response.json()["data"]["movies"]
                return returnObj
            else:
                returnObj["result"] = -1
                returnObj["description"] = "search:: couldn't find any movies"
                return returnObj
        else:
            returnObj["result"] = -1
            returnObj["description"] = "search:: bad response"
            return returnObj

if __name__ == "__main__":
    testObj = YTSController()
    x = testObj.search("Avengers (2012)")
    if x["result"] != 0:
        print(x["description"])
    else:
        print(x["data"]["title"])
    x = testObj.search("Frozen (2013)")
    if x["result"] != 0:
        print(x["description"])
    else:
        print(x["data"]["title"])
    x = testObj.search("Frozen 2 (2019)")
    if x["result"] != 0:
        print(x["description"])
    else:
        print(x["data"]["title"])
    x = testObj.search("Parasite")
    if x["result"] != 0:
        print(x["description"])
    else:
        print(x["data"]["title"])