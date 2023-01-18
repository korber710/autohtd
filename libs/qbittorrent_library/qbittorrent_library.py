from os import environ
from qbittorrent import Client
import logging

# Setup logger
logger = logging.getLogger()

class QBittorrentController:
    def __init__(self, ip="192.168.1.197", port=8113, password="admin"):
        self.cookies = None
        self.password = password
        self.requestID = 0
        self.ip = ip
        self.port = port
        self.qb = Client("http://{}:{}/".format(self.ip, self.port))
    def login(self):
        returnObj = {
            "result": -1,
            "description": "",
            "data": ""
        }
        logger.info("Logging in to QBittorrent")
        try:
            self.qb.login("admin", self.password)
        except Exception as e:
            returnObj["result"] = -1
            returnObj["description"] = "login:: failed to login"
            logger.exception(e)
            return returnObj
        returnObj["result"] = 0
        returnObj["description"] = "login successful"
        logger.info("Login successful")
        return returnObj
    def addTorrent(self, magnet):
        returnObj = {
            "result": -1,
            "description": "",
            "data": ""
        }
        logger.info("Adding torrent")
        try:
            self.qb.download_from_link(magnet)
        except Exception as e:
            returnObj["result"] = -1
            returnObj["description"] = "addTorrent:: failed to add torrent"
            logger.exception(e)
            return returnObj
        torrentID = magnet.split("magnet:?xt=urn:btih:")[1].split("&")[0].lower()
        returnObj["result"] = 0
        returnObj["description"] = "addTorrent successful"
        returnObj["data"] = str(torrentID)
        logger.info(f"Torrent added - {torrentID}")
        return returnObj
    def removeTorrent(self, id):
        returnObj = {
            "result": -1,
            "description": "",
            "data": ""
        }
        logger.info(f"Removing torrent {id}")
        try:
            self.qb.delete(id)
        except Exception as e:
            returnObj["result"] = -1
            returnObj["description"] = "removeTorrent:: failed to remove"
            logger.exception(e)
            return returnObj
        returnObj["result"] = 0
        returnObj["description"] = "removeTorrent successful"
        logger.info("Torrent removed")
        return returnObj
    def getTorrents(self):
        returnObj = {
            "result": -1,
            "description": "",
            "data": ""
        }
        logger.info("Getting torrents")
        try:
            torrents = self.qb.torrents()
        except Exception as e:
            returnObj["result"] = -1
            returnObj["description"] = "getTorrents:: failed to get torrents"
            logger.exception(e)
            return returnObj
        returnObj["result"] = 0
        returnObj["description"] = "getTorrents successful"
        returnObj["data"] = torrents
        logger.info("Successfully got torrents")
        return returnObj
    def getTorrentFiles(self, id):
        returnObj = {
            "result": -1,
            "description": "",
            "data": ""
        }
        logger.info("Getting torrent files")
        try:
            results = self.qb.get_torrent_files(id)
        except Exception as e:
            returnObj["result"] = -1
            returnObj["description"] = "getTorrentFiles:: failed to send request"
            logger.exception(e)
            return returnObj
        returnObj["result"] = 0
        returnObj["description"] = "getTorrentFiles successful"
        returnObj["data"] = results
        logger.info("Successfully got torrent files")
        return returnObj

if __name__ == "__main__":
    testObj = QBittorrentController(ip="192.168.50.35")
    x = testObj.login()
    print(x)
    x = testObj.getTorrents()
    print(x)
    x = testObj.addTorrent('magnet:?xt=urn:btih:D565CA1A81523F0DBA4F9E5CEA4EA3B492CABDC8&dn=Snowpiercer.S01E02.HDTV.x264-KILLERS%5BTGx%5D+%E2%AD%90&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.iamhansen.xyz%3A2000%2Fannounce&tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&tr=udp%3A%2F%2Fipv4.tracker.harry.lu%3A80%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.zer0day.to%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fcoppersurfer.tk%3A6969%2Fannounce')
    print(x)
    info = x["data"]
    x = testObj.getTorrentFiles(info)
    print(x)
    # x = testObj.removeTorrent(info)
    # print(x)
