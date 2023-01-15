############################################################
#
#   Auto Home Torrent Downloader App for TV Shows
#   created by Steve Korber
#   korbersa@outlook.com
#
############################################################

# import
import time
from datetime import datetime
from datetime import timedelta
import psycopg2
import json
import os
import shutil
import pytz
import difflib
import argparse

# add custom libs
from qbittorrent_library.qbittorrent_library import QBittorrentController
from torrent_library.torrent_library import TorrentController
from episodate_library.episodate_library import *

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--host-ip', help='The IP used for the torrent client and the PostgreSQL server')
parser.add_argument('--db-secret', help='PostgreSQL username:password')
args = parser.parse_args()

# constants
EST = pytz.timezone("US/Eastern")
GMT = pytz.timezone("GMT")
HOST_IP = args.host_ip
POSTGRES_USER = args.db_secret.split(":")[0]
POSTGRES_PASSWORD = args.db_secret.split(":")[1]

# header
print("\n\n==============================\nAuto TV Torrent Application\n==============================\n\n", flush=True)
torrent_count = 0

# main loop
while(True):
    if (datetime.now().astimezone(EST).hour > 7) and (datetime.now().astimezone(EST).hour < 23):
        # create tv search object
        try:
            tv_search_client = TVSearchController()
        except:
            print("tv database error", flush=True)
            continue
        
        # create torrent client object
        torrent_client = QBittorrentController(ip=HOST_IP)
        results = torrent_client.login()
        if results["result"] != 0:
            print(results["description"], flush=True)
            continue

        # create torrent search object
        torrent_search_client = TorrentController()

        # connect to the database
        conn = psycopg2.connect(user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=HOST_IP, port="5432", database="home")
        cur = conn.cursor()

        # grab entries from tv_shows database
        cur.execute("SELECT * FROM public.tv_shows")
        items = cur.fetchall()
        print(items)

        # get active torrents
        results = torrent_client.getTorrents()
        print("getTorrents: {}".format(results), flush=True)
        if results["result"] != 0:
            print(results["description"], flush=True)
            continue
        else:
            torrent_count = len(results["data"])
        print("\nTorrent Count: {}\n".format(torrent_count), flush=True)

        # loop through tv_shows table
        for item in items:
            ### check pytv database for the show and get season
            # result = db.search(item[1], 'en')
            try:
                results = tv_search_client.search(item[1])
            except:
                print("error searching tv db for {}".format(item[1]), flush=True)
                continue
            if results["result"] != 0:
                print("could not find {} in tv db".format(item[1]), flush=True)
                continue
            show_obj = results["data"]
            show_list = []
            try:
                for show in show_obj["tv_shows"]:
                    if show["country"] in ["CA", "US"]:
                        show_list.append(show["name"])
                    else:
                        show_list.append("")
                best_show = difflib.get_close_matches(item[1], show_list)[0]
                show_index = show_list.index(best_show)
                # print(show_obj, flush=True)
            except Exception as e:
                best_show = item[1]
                print(e, flush=True)
            # showID = result[showObj[bestShow]]["id"]
            print("\n\nBest show: {}".format(best_show), flush=True)
            try:
                # show = db[showID]
                results = tv_search_client.lookup(show_obj["tv_shows"][show_index]["id"])
                show_details = results["data"]["tvShow"]
                season_list = get_season_numbers(show_details)
            except Exception as e:
                print(e, flush=True)
                print("show id not found {}".format(show_obj["tv_shows"][show_index]["id"]), flush=True)
                continue
            try:
                # season = show[item[2]]
                season = get_season_episodes(show_details, item[2])
            except Exception as e:
                print(e, flush=True)
                print("issue getting season {}".format(item[2]), flush=True)
                print("show: {}".format(show), flush=True)
                continue
            data = item[4]
            print("\n==============================\n{}\n{}\n==============================\n".format(item[1], best_show), flush=True)
            # print(len(season))
            ### loop through each episode of the season
            for episode in season:
                ### generate episode id
                # episodeID = str(episode).replace(">", "").replace("-", "").split()[1].replace("S0", "S").replace("E0", "E")
                # episodeID = str(season[episode]).split("-")[0].replace("<", "").split()[1]
                # episodeID = "S{}E{}".format(episodeID.split("x")[0], episodeID.split("x")[1])
                episodeID = "S{:02d}E{:02d}".format(episode["season"], episode["episode"])
                # print(episodeID, flush=True)
                # print(episodeID)
                episodeExists = False
                ### loop through episodes in local database
                for episodeData in data["episodes"]:
                    ### check episode air date is before today
                    try:
                        # firstAiredDate = datetime.strptime(season[episode]["firstAired"], "%Y-%m-%d").date()
                        firstAiredDate = datetime.strptime(episode["air_date"], "%Y-%m-%d %H:%M:%S")
                        firstAiredDate = GMT.localize(firstAiredDate)
                    except:
                        # print("first aired: {}".format(season[episode]["firstAired"]), flush=True)
                        firstAiredDate = datetime.today().astimezone(EST) - timedelta(days=1)
                    if firstAiredDate.astimezone(EST).date() < datetime.today().astimezone(EST).date():
                        ### compare episode id
                        if episodeID == episodeData["episodeID"]:
                            print(f"Episode: {episodeID}, Date Computed: {firstAiredDate.astimezone(EST).date()}, Date: {episode['air_date']}", flush=True)
                            episodeExists = True
                            ### check if the episode has been downloaded
                            if episodeData["completed"] == False:
                                ### check if the torrent has been completed
                                if episodeData["torrentID"] == "":
                                    if (torrent_count < 16):
                                        ### search for torrent with show name and episode id
                                        if item[1] == "Big Brother":
                                            searchQuery = '{} US {}'.format(item[1], episodeID)
                                        elif item[1] == "Celebrity Big Brother (US)":
                                            searchQuery = 'Celebrity Big Brother US {}'.format(episodeID)
                                        elif item[1] == "The Bachelor Presents Listen to Your Heart":
                                            searchQuery = 'The Bachelor Listen to Your Heart {}'.format(episodeID)
                                        elif item[1] == "The Bachelor The Greatest Seasons — Ever!":
                                            searchQuery = 'The Bachelor The Greatest Seasons Ever {}'.format(episodeID)
                                        else:
                                            searchQuery = '{} {}'.format(item[1], episodeID)
                                        results = torrent_search_client.ottsx_search(searchQuery)
                                        if results["result"] != 0:
                                            print(results["description"], flush=True)
                                            continue
                                        magnetLink = results["data"]
                                        print(magnetLink, flush=True)
                                        results = torrent_client.addTorrent(magnetLink)
                                        if results["result"] != 0:
                                            print(results["description"], flush=True)
                                            continue
                                        torrent_count += 1
                                        torrentID = results["data"]
                                        print("torrent ID: {}".format(torrentID), flush=True)
                                        results = torrent_client.getTorrentFiles(torrentID)
                                        print(results, flush=True)
                                        ### push torrent id to database
                                        for i in data["episodes"]:
                                            if i["episodeID"] == episodeID:
                                                i["torrentID"] = torrentID
                                        cur.execute("UPDATE public.tv_shows SET data = '{}' WHERE id = {}".format(json.dumps(data), item[0]))
                                        updatedRows = cur.rowcount
                                        print("updated rows {}".format(updatedRows), flush=True)
                                        conn.commit()
                                ### torrent hasn't been completed
                                else:
                                    ### if torrent done delete and move file
                                    print("check torrent", flush=True)
                                    results = torrent_client.getTorrents()
                                    content = ""
                                    for torr in results["data"]:
                                        if torr["hash"] == episodeData["torrentID"]:
                                            content = torr
                                    if content == "":
                                        print("cannot find hash in torrents", flush=True)
                                        continue
                                    if 0.999 < content["progress"] < 1.001:
                                        print("complete")
                                        downloadedPath = content["save_path"]
                                        torrentName = content["name"]
                                        # check if dir
                                        if os.path.isdir(os.path.join(downloadedPath, torrentName)):
                                            print("dir")
                                            isDir = True
                                            parentDir = torrentName
                                            ### find largest file and make that filename, need to delete dir after
                                            results = torrent_client.getTorrentFiles(episodeData["torrentID"])
                                            size = 0
                                            largestFile = None
                                            for folderContent in results["data"]:
                                                if folderContent["size"] > size:
                                                    size = folderContent["size"]
                                                    largestFile = folderContent
                                            torrentFilename = largestFile["name"]
                                            print("torrentFilename: {}".format(torrentFilename), flush=True)
                                            if os.path.exists(os.path.join(downloadedPath, parentDir)):
                                                print("parent path to remove exists")
                                            else:
                                                print("parent path to remove is bad")
                                                continue
                                        else:
                                            print("file")
                                            isDir = False
                                            torrentFilename = content["name"]
                                        torrentPath = os.path.join(downloadedPath, torrentFilename)
                                        print("path: {}".format(torrentPath))
                                        if os.path.exists(torrentPath):
                                            ### check path on database
                                            if os.path.exists(os.path.join(os.sep, *item[3].split(","))) == False:
                                                print("path doesn't exist")
                                                print(os.path.join(os.sep, *item[3].split(",")))
                                                try:
                                                    os.makedirs(os.path.join(os.sep, *item[3].split(",")))
                                                except:
                                                    print("error making dir")
                                                    continue
                                                if os.path.exists(os.path.join(os.sep, *item[3].split(","))) == False:
                                                    print("path still doesn't exist")
                                                    continue
                                            ### delete torrent
                                            results = torrent_client.removeTorrent(episodeData["torrentID"])
                                            torrent_count -= 1
                                            print(results)
                                            for i in data["episodes"]:
                                                if i["episodeID"] == episodeID:
                                                    i["torrentID"] = ""
                                                    i["completed"] = True
                                            cur.execute("UPDATE public.tv_shows SET data = '{}' WHERE id = {}".format(json.dumps(data), item[0]))
                                            updatedRows = cur.rowcount
                                            print("updated rows {}".format(updatedRows))
                                            conn.commit()
                                            shutil.move(torrentPath, os.path.join(os.sep, *item[3].split(",")))
                                            print("copied {} to {}".format(torrentPath, os.path.join(os.sep, *item[3].split(","))))
                                            if isDir:
                                                if os.path.exists(os.path.join(downloadedPath, parentDir)):
                                                    shutil.rmtree(os.path.join(downloadedPath, parentDir))
                                                    print("removed parent path")
                                    else:
                                        print("not complete - progress {}".format(100 * content["progress"]))
                ### create episode entry in database because it didn't find it
                if episodeExists == False:
                    try:
                        # firstAiredDate = datetime.strptime(season[episode]["firstAired"], "%Y-%m-%d").date()
                        firstAiredDate = datetime.strptime(episode["air_date"], "%Y-%m-%d %H:%M:%S")
                        firstAiredDate = GMT.localize(firstAiredDate)
                    except:
                        # print("first aired: {}".format(season[episode]["firstAired"]), flush=True)
                        firstAiredDate = datetime.today().astimezone(EST) - timedelta(days=1)
                    print(f"Episode: {episodeID}, Date Computed: {firstAiredDate.astimezone(EST).date()}, Date: {episode['air_date']}", flush=True)
                    if firstAiredDate.astimezone(EST).date() < datetime.today().astimezone(EST).date():
                        ### create entry
                        print("need to create {}".format(episodeID))
                        data["episodes"].append({"episodeID": episodeID, "torrentID": "", "completed": False})
                        cur.execute("UPDATE public.tv_shows SET data = '{}' WHERE id = {}".format(json.dumps(data), item[0]))
                        updatedRows = cur.rowcount
                        print("updated rows {}".format(updatedRows))
                        conn.commit()
                        ### search for torrent with show name and episode id
                        if item[1] == "Big Brother":
                            searchQuery = '{} US {}'.format(item[1], episodeID)
                        elif item[1] == "Celebrity Big Brother (US)":
                            searchQuery = 'Celebrity Big Brother US {}'.format(episodeID)
                        elif item[1] == "The Bachelor Presents Listen to Your Heart":
                            searchQuery = 'The Bachelor Listen to Your Heart {}'.format(episodeID)
                        elif item[1] == "The Bachelor The Greatest Seasons — Ever!":
                            searchQuery = 'The Bachelor The Greatest Seasons Ever {}'.format(episodeID)
                        else:
                            searchQuery = '{} {}'.format(item[1], episodeID)
                        results = torrent_search_client.ottsx_search(searchQuery)
                        if results["result"] != 0:
                            print(results["description"])
                            continue
                        magnetLink = results["data"]
                        print(magnetLink, flush=True)
                        # if len(torrents) == 0:
                        #     print("no torrents for {} {}".format(item[1], episodeID))
                        # else:
                        if (torrent_count < 16):
                            # torrent = torrents.getBestTorrent(min_seeds=5, min_filesize='200 MiB', max_filesize='1 GiB')
                            # if torrent == None:
                            #     print("didn't find any that met criteria")
                            #     continue
                            # print(torrent.title)
                            results = torrent_client.addTorrent(magnetLink)
                            # print(torrent.filesize)
                            if results["result"] != 0:
                                print(results["description"])
                                continue
                            torrent_count += 1
                            torrentID = results["data"]
                            print("torrent ID: {}".format(torrentID))
                            results = torrent_client.getTorrents()
                            print(results)
                            ### push torrent id to database
                            for i in data["episodes"]:
                                if i["episodeID"] == episodeID:
                                    i["torrentID"] = torrentID
                            cur.execute("UPDATE public.tv_shows SET data = '{}' WHERE id = {}".format(json.dumps(data), item[0]))
                            updatedRows = cur.rowcount
                            print("updated rows {}".format(updatedRows))
                            conn.commit()

    # wait 1 hour
    print("\n\n==============================\nlooping\n==============================\n\n", flush=True)
    print(f"loop start -- {datetime.now().astimezone(EST)}", flush=True)
    time.sleep(3600)
    # time.sleep(10)
    print("\n\n", flush=True)
