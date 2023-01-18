############################################################
#
#   Auto Home Torrent Downloader App for Movies
#   created by Steve Korber
#   korbersa@outlook.com
#
############################################################

# import
import time
from datetime import datetime
import psycopg2
import json
import os
import shutil
import pytz
import urllib
import argparse

# add custom libs
from qbittorrent_library.qbittorrent_library import QBittorrentController
from yts_library.yts_library import YTSController

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--host-ip', help='The IP used for the torrent client and the PostgreSQL server')
parser.add_argument('--db-secret', help='PostgreSQL username:password')
args = parser.parse_args()

# constants
EST = pytz.timezone("US/Eastern")
HOST_IP = args.host_ip
POSTGRES_USER = args.db_secret.split(":")[0]
POSTGRES_PASSWORD = args.db_secret.split(":")[1]

# header
print("\n\n==============================\nAuto Movie Torrent Application\n==============================\n\n", flush=True)
torrent_count = 0

############################################################
# main loop
###
while(True):
    if (datetime.now().astimezone(EST).hour > 7) and (datetime.now().astimezone(EST).hour < 23):
        # create objects and setup
        delugeObj = QBittorrentController(ip=HOST_IP)
        ytsObj = YTSController()
        results = delugeObj.login()
        if results["result"] != 0:
            print(results["description"], flush=True)
            continue
        
        # connect to the db
        conn = psycopg2.connect(user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=HOST_IP, port="5432", database="home")
        cur = conn.cursor()
        
        # grab entries from tv_shows database
        cur.execute("SELECT * FROM public.movies")
        items = cur.fetchall()
        print(items)

        results = delugeObj.getTorrents()
        print("getTorrents: {}".format(results), flush=True)
        if results["result"] != 0:
            print(results["description"], flush=True)
            continue
        else:
            torrent_count = len(results["data"])
        print("\nTorrent Count: {}\n".format(torrent_count), flush=True)
        ### loop through movies
        for item in items:
            print("\n==============================\n{}\n==============================\n".format(item[1]), flush=True)
            ### check if data exists
            if not item[3]:
                ### create entry
                print("need to create data")
                newData = {"torrentID": "", "completed": False}
                cur.execute("UPDATE public.movies SET data = '{}' WHERE id = {}".format(json.dumps(newData), item[0]))
                updatedRows = cur.rowcount
                print("updated rows {}".format(updatedRows))
                conn.commit()
                continue
            ### check if there is a torrent
            data = item[3]
            if data["torrentID"] == "":
                if data["completed"] == False:
                    ### check yts for movie
                    results = ytsObj.search(item[1])
                    if results["result"] != 0:
                        print(results["description"])
                        continue
                    print("retreived torrent name: {}".format(results["data"]["title_long"]), flush=True)
                    ### add torrent to list
                    chosenTorrent = None
                    for torrent in results["data"]["torrents"]:
                        if torrent["quality"] == "1080p":
                            chosenTorrent = torrent
                    if not chosenTorrent:
                        chosenTorrent = results["data"]["torrents"][0]
                    encodedName = urllib.parse.quote(results["data"]["title_long"])
                    magnetLink = "magnet:?xt=urn:btih:{}&dn={}&tr=udp://tracker.cyberia.is:6969/announce&tr=udp://tracker.port443.xyz:6969/announce&tr=http://tracker3.itzmx.com:6961/announce&tr=udp://tracker.moeking.me:6969/announce&tr=http://vps02.net.orel.ru:80/announce&tr=http://tracker.openzim.org:80/announce&tr=udp://tracker.skynetcloud.tk:6969/announce&tr=https://1.tracker.eu.org:443/announce&tr=https://3.tracker.eu.org:443/announce&tr=http://re-tracker.uz:80/announce&tr=https://tracker.parrotsec.org:443/announce&tr=udp://explodie.org:6969/announce&tr=udp://tracker.filemail.com:6969/announce&tr=udp://tracker.nyaa.uk:6969/announce&tr=udp://retracker.netbynet.ru:2710/announce&tr=http://tracker.gbitt.info:80/announce&tr=http://tracker2.dler.org:80/announce".format(chosenTorrent["hash"].lower(), encodedName)
                    results = delugeObj.addTorrent(magnetLink)
                    if results["result"] != 0:
                        print("error adding torrent")
                        continue
                    print("added torrent")
                    torrent_count += 1
                    torrentID = chosenTorrent["hash"].lower()
                    print("torrent ID: {}".format(torrentID), flush=True)
                    time.sleep(1)
                    results = delugeObj.getTorrentFiles(torrentID)
                    if results["result"] != 0:
                        print("error getting torrents")
                        continue
                    print(results, flush=True)
                    ### push torrent id to database
                    newData = {"torrentID": torrentID, "completed": False}
                    cur.execute("UPDATE public.movies SET data = '{}' WHERE id = {}".format(json.dumps(newData), item[0]))
                    updatedRows = cur.rowcount
                    print("updated rows {}".format(updatedRows), flush=True)
                    conn.commit()
            else:
                if data["completed"] == False:
                    ### check torrent
                    print("check torrent - {}".format(data["torrentID"]), flush=True)
                    results = delugeObj.getTorrents()
                    content = ""
                    # print(results, flush=True)
                    if results["result"] != 0:
                        print(results["description"], flush=True)
                        continue
                    for torr in results["data"]:
                        if torr["hash"] == data["torrentID"]:
                            content = torr
                    if content == "":
                        print("cannot find hash in torrents", flush=True)
                        continue
                    if 0.999 < content["progress"] < 1.001:
                        time.sleep(1)
                        print("complete", flush=True)
                        # results = delugeObj.getTorrents([data["torrentID"]])
                        # downloadedPath = results["data"]["result"]["torrents"][0]["save_path"]
                        downloadedPath = content["save_path"]
                        torrentName = content["name"]
                        if os.path.isdir(os.path.join(downloadedPath, torrentName)):
                            print("dir")
                            isDir = True
                            parentDir = torrentName
                        else:
                            print("file")
                            print("=================\nneed to add code\n=================")
                            continue
                        torrentPath = os.path.join(downloadedPath, item[1])
                        print("path: {}".format(torrentPath), flush=True)
                        if not os.path.exists(os.path.join(downloadedPath, item[1])):
                            try:
                                os.rename(os.path.join(downloadedPath, parentDir), os.path.join(downloadedPath, item[1]))
                            except:
                                print("cannot rename folder", flush=True)
                                continue
                            print("tried to rename folder", flush=True)
                            if os.path.exists(os.path.join(downloadedPath, item[1])):
                                print("rename worked", flush=True)
                            else:
                                print("rename did not work", flush=True)
                                continue
                        if os.path.exists(torrentPath):
                            ### delete torrent
                            results = delugeObj.removeTorrent(data["torrentID"])
                            if results["result"] != 0:
                                print("couldn't remove torrent", flush=True)
                                continue
                            torrent_count -= 1
                            print("deleted torrent", flush=True)
                            finishedData = {"torrentID": "", "completed": True}
                            cur.execute("UPDATE public.movies SET data = '{}' WHERE id = {}".format(json.dumps(finishedData), item[0]))
                            updatedRows = cur.rowcount
                            print("updated rows {}".format(updatedRows))
                            conn.commit()
                            # print(results)
                            if os.path.exists(os.path.join(os.sep, *item[2].split(","), item[1])):
                                shutil.rmtree(torrentPath)
                                print("movie already exists {}, deleted torrent download {}".format(os.path.join(os.sep, *item[2].split(","), item[1]), torrentPath), flush=True)
                            else:
                                shutil.move(torrentPath, os.path.join(os.sep, *item[2].split(","),))
                                print("copied {} to {}".format(torrentPath, os.path.join(os.sep, *item[2].split(","))))
                    else:
                        print("not complete - progress {}".format(100 * content[contentKey]["progress"]))

    # wait 1 hour
    print("\n\n==============================\nlooping\n==============================\n\n", flush=True)

    print(f"loop start -- {datetime.now().astimezone(EST)}", flush=True)
    time.sleep(3600)
    # time.sleep(10)
    print("\n\n", flush=True)