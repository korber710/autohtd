from tpblite import TPB
from tpblite import CATEGORIES, ORDERS
from gazpacho import get
from gazpacho import Soup
from urllib.parse import quote_plus

class TorrentController:
    def __init__(self, url='tpb.party'):
        self.t = TPB(url)
    
    def pirate_bay_search(self, search_param, orderParam=ORDERS.SEEDERS.ASC):
        returnObj = {
            "result": -1,
            "description": "",
            "data": ""
        }
        try:
            torrents = self.t.search(search_param, order=orderParam)
        except:
            returnObj["result"] = -1
            returnObj["description"] = "search:: failed to send request"
            return returnObj
        returnObj["result"] = 0
        returnObj["description"] = "search successful"
        returnObj["data"] = torrents
        return returnObj
    
    def ottsx_search(self, search_param):
        returnObj = {
            "result": -1,
            "description": "",
            "data": ""
        }
        url_search = quote_plus(search_param.lower())
        url = "https://1337x.to/search/{}/1/".format(url_search)
        print(f"URL: {url}")
        try:
            html = get(url)
        except Exception as exc:
            print(f"{type(exc).__name__} error occurred - {exc}")
            returnObj["result"] = -1
            returnObj["description"] = "ottsx_search:: cannot get html"
            return returnObj
        soup = Soup(html)
        results = soup.find('td', {'class': 'coll-1 name'})
        try:
            if len(results) == 0:
                returnObj["result"] = -1
                returnObj["description"] = "ottsx_search:: could not find anything"
                return returnObj
            result = results[0]
        except:
            print(results)
            result = results
        try:
            torrentUrl = Soup(result.html).find('a')[1].attrs["href"]
        except:
            print(results)
            returnObj["result"] = -1
            returnObj["description"] = "ottsx_search:: no html object"
            return returnObj
        url = "https://1337x.to{}".format(torrentUrl)
        print(url)
        html = get(url)
        soup = Soup(html)

        # try to find 'a' within box-info
        try:
            magnetSearch = Soup(soup.find('div', {'class': 'box-info torrent-detail-page  vpn-info-wrap'}).html).find('a')
            for i in magnetSearch:
                if i.attrs['href'].startswith("magnet"):
                    magnetLink = i.attrs['href']
        except:
            returnObj["result"] = -1
            returnObj["description"] = "ottsx_search:: could not find magnet link"
            return returnObj
        returnObj["result"] = 0
        returnObj["description"] = "ottsx_search successful"
        returnObj["data"] = str(magnetLink)
        return returnObj

if __name__ == "__main__":
    testObj = TorrentController()
    x = testObj.ottsx_search("American Idol S19E10")
    print(x)