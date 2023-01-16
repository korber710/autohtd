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
import sys
import logging

# setup logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger_format = logging.Formatter('%(asctime)s [%(levelname)s]\t%(message)s')
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logger_format)
logger.addHandler(handler)

# add custom libs
from qbittorrent_library.qbittorrent_library import QBittorrentController
from torrent_library.torrent_library import TorrentController
from episodate_library.episodate_library import *

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--host-ip', help='The IP used for the torrent client and the PostgreSQL server')
parser.add_argument('--db-secret', help='PostgreSQL username:password')
parser.add_argument('--torrent-client-secret', help='Password for torrent client')
args = parser.parse_args()

# constants
EST = pytz.timezone("US/Eastern")
GMT = pytz.timezone("GMT")
HOST_IP = args.host_ip
POSTGRES_USER = args.db_secret.split(":")[0]
POSTGRES_PASSWORD = args.db_secret.split(":")[1]
TORRENT_CLIENT_PASSWORD = args.torrent_client_secret

# header
print("\n\n==============================\nAuto TV Torrent Application\n==============================\n\n", flush=True)
torrent_count = 0

# main loop
while(True):
    if (datetime.now().astimezone(EST).hour > 7) and (datetime.now().astimezone(EST).hour < 23):
        # create tv search object
        try:
            logger.info("Connecting to search client API")
            tv_search_client = TVSearchController()
        except Exception as e:
            logger.exception(e)
            continue
        
        # create torrent client object
        torrent_client = QBittorrentController(ip=HOST_IP, password=TORRENT_CLIENT_PASSWORD)
        results = torrent_client.login()
        if results["result"] != 0:
            continue

        # create torrent search object
        torrent_search_client = TorrentController()

        # connect to the database
        conn = psycopg2.connect(user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=HOST_IP, port="5432", database="home")
        cur = conn.cursor()

        # grab entries from tv_shows database
        cur.execute("SELECT * FROM public.tv_shows")
        items = cur.fetchall()

        # get active torrents
        results = torrent_client.getTorrents()
        if results["result"] != 0:
            torrent_count = 0
            continue
        torrent_count = len(results["data"])
        logger.info(f"Torrent Count: {torrent_count}")

        # loop through tv_shows table
        for item in items:
            # check tv database for the show and get season
            try:
                results = tv_search_client.search(item[1])
            except Exception as e:
                logger.exception(e)
                continue
            if results["result"] != 0:
                logger.warn(f"Could not find {item[1]} in tv db")
                continue

            # set the show object and get show names
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
            except Exception as e:
                best_show = item[1]
                logger.exception(e)
            logger.info(f"Best show: {best_show}")

            # Get the episodes in the season for the best matching show
            try:
                results = tv_search_client.lookup(show_obj["tv_shows"][show_index]["id"])
                show_details = results["data"]["tvShow"]
                season_list = get_season_numbers(show_details)
            except Exception as e:
                logger.exception(e)
                logger.error(f"Show id not found {show_obj['tv_shows'][show_index]['id']}")
                continue
            try:
                season = get_season_episodes(show_details, item[2])
            except Exception as e:
                logger.exception(e)
                logger.debug(f"Issue getting season {item[2]}")
                logger.debug(f"Show: {show}")
                continue

            # set current episode data from database to variable
            data = item[4]
            
            print("\n==============================\n{}\n{}\n==============================\n".format(item[1], best_show), flush=True)

            # loop through each episode of the season
            for episode in season:
                # generate episode id
                episodeID = "S{:02d}E{:02d}".format(episode["season"], episode["episode"])
                episodeExists = False

                # loop through episodes in local database
                for episodeData in data["episodes"]:
                    # check episode air date is before today
                    try:
                        firstAiredDate = datetime.strptime(episode["air_date"], "%Y-%m-%d %H:%M:%S")
                        firstAiredDate = GMT.localize(firstAiredDate)
                    except:
                        firstAiredDate = datetime.today().astimezone(EST) - timedelta(days=1)
                    
                    if firstAiredDate.astimezone(EST).date() < datetime.today().astimezone(EST).date():
                        # compare episode id
                        if episodeID == episodeData["episodeID"]:
                            logger.info(f"Episode: {episodeID}, Date: {firstAiredDate.astimezone(EST).date()}")
                            episodeExists = True

                            # check if the episode has been downloaded
                            if episodeData["completed"] == False:
                                # check if the torrent has been completed
                                if episodeData["torrentID"] == "":
                                    if (torrent_count < 8):
                                        # search for torrent with show name and episode id
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
                                        
                                        # search for the episode on the torrent site
                                        results = torrent_search_client.ottsx_search(searchQuery)
                                        if results["result"] != 0:
                                            continue

                                        # create a magnet link for the torrent client
                                        magnetLink = results["data"]
                                        logger.debug(f"Magnet Link: {magnetLink}")
                                        results = torrent_client.addTorrent(magnetLink)
                                        if results["result"] != 0:
                                            continue
                                        
                                        # Increment the torrent counter
                                        # TODO: check if the new torrent ID exists in the torrent client first
                                        torrent_count += 1
                                        torrentID = results["data"]
                                        logger.debug(f"Torrent ID: {torrentID}")
                                        results = torrent_client.getTorrentFiles(torrentID)
                                        logger.debug(results)

                                        # push torrent id to database
                                        for i in data["episodes"]:
                                            if i["episodeID"] == episodeID:
                                                i["torrentID"] = torrentID
                                        cur.execute("UPDATE public.tv_shows SET data = '{}' WHERE id = {}".format(json.dumps(data), item[0]))
                                        updatedRows = cur.rowcount
                                        logger.info(f"Updated rows {updatedRows}")
                                        conn.commit()

                                # torrent hasn't been completed
                                else:
                                    # if torrent done delete and move file
                                    logger.info("Check torrent")
                                    results = torrent_client.getTorrents()
                                    content = ""
                                    for torr in results["data"]:
                                        if torr["hash"] == episodeData["torrentID"]:
                                            content = torr
                                    if content == "":
                                        logger.error("Cannot find hash in torrents")
                                        continue
                                    if 0.999 < content["progress"] < 1.001:
                                        logger.info("The torrent is complete")
                                        downloadedPath = content["save_path"]
                                        torrentName = content["name"]
                                        # check if dir
                                        if os.path.isdir(os.path.join(downloadedPath, torrentName)):
                                            logger.debug("dir")
                                            isDir = True
                                            parentDir = torrentName
                                            # find largest file and make that filename, need to delete dir after
                                            results = torrent_client.getTorrentFiles(episodeData["torrentID"])
                                            size = 0
                                            largestFile = None
                                            for folderContent in results["data"]:
                                                if folderContent["size"] > size:
                                                    size = folderContent["size"]
                                                    largestFile = folderContent
                                            torrentFilename = largestFile["name"]
                                            logger.info(f"torrentFilename: {torrentFilename}")
                                            if os.path.exists(os.path.join(downloadedPath, parentDir)):
                                                logger.debug("Parent path to remove exists")
                                            else:
                                                logger.error("Parent path to remove is bad")
                                                continue
                                        else:
                                            logger.debug("file")
                                            isDir = False
                                            torrentFilename = content["name"]
                                        torrentPath = os.path.join(downloadedPath, torrentFilename)
                                        logger.debug(f"path: {torrentPath}")
                                        if os.path.exists(torrentPath):
                                            # check path on database
                                            if os.path.exists(os.path.join(os.sep, *item[3].split(","))) == False:
                                                logger.warn("Path doesn't exist")
                                                logger.debug(os.path.join(os.sep, *item[3].split(",")))
                                                try:
                                                    os.makedirs(os.path.join(os.sep, *item[3].split(",")))
                                                except Exception as e:
                                                    logger.exception(e)
                                                    continue
                                                if os.path.exists(os.path.join(os.sep, *item[3].split(","))) == False:
                                                    logger.error("Path still doesn't exist")
                                                    continue
                                            
                                            # delete torrent
                                            _ = torrent_client.removeTorrent(episodeData["torrentID"])
                                            torrent_count -= 1
                                            for i in data["episodes"]:
                                                if i["episodeID"] == episodeID:
                                                    i["torrentID"] = ""
                                                    i["completed"] = True
                                            cur.execute("UPDATE public.tv_shows SET data = '{}' WHERE id = {}".format(json.dumps(data), item[0]))
                                            updatedRows = cur.rowcount
                                            logger.debug(f"Updated rows {updatedRows}")
                                            conn.commit()
                                            shutil.move(torrentPath, os.path.join(os.sep, *item[3].split(",")))
                                            logger.info(f"Copied {torrentPath} to {os.path.join(os.sep, *item[3].split(','))}")
                                            if isDir:
                                                if os.path.exists(os.path.join(downloadedPath, parentDir)):
                                                    shutil.rmtree(os.path.join(downloadedPath, parentDir))
                                                    logger.debug("Removed parent path")
                                    else:
                                        logger.info(f"Torrent not complete - progress {100 * content['progress']}")

                # create episode entry in database because it didn't find it
                if episodeExists == False:
                    try:
                        firstAiredDate = datetime.strptime(episode["air_date"], "%Y-%m-%d %H:%M:%S")
                        firstAiredDate = GMT.localize(firstAiredDate)
                    except:
                        firstAiredDate = datetime.today().astimezone(EST) - timedelta(days=1)
                    logger.info(f"Episode: {episodeID}, Date Computed: {firstAiredDate.astimezone(EST).date()}, Date: {episode['air_date']}")

                    if firstAiredDate.astimezone(EST).date() < datetime.today().astimezone(EST).date():
                        # create entry
                        logger.info(f"Need to create {episodeID}")
                        data["episodes"].append({"episodeID": episodeID, "torrentID": "", "completed": False})
                        cur.execute("UPDATE public.tv_shows SET data = '{}' WHERE id = {}".format(json.dumps(data), item[0]))
                        updatedRows = cur.rowcount
                        logger.debug(f"Updated rows {updatedRows}")
                        conn.commit()

                        # search for torrent with show name and episode id
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
                        
                        # search for the torret on the web
                        results = torrent_search_client.ottsx_search(searchQuery)
                        if results["result"] != 0:
                            continue
                        magnetLink = results["data"]
                        logger.debug(f"Magnet Link: {magnetLink}")

                        if (torrent_count < 8):
                            results = torrent_client.addTorrent(magnetLink)
                            if results["result"] != 0:
                                continue
                            torrent_count += 1
                            torrentID = results["data"]
                            logger.info(f"Torrent ID: {torrentID}")
                            results = torrent_client.getTorrents()

                            # push torrent id to database
                            for i in data["episodes"]:
                                if i["episodeID"] == episodeID:
                                    i["torrentID"] = torrentID
                            cur.execute("UPDATE public.tv_shows SET data = '{}' WHERE id = {}".format(json.dumps(data), item[0]))
                            updatedRows = cur.rowcount
                            logger.info(f"Updated rows {updatedRows}")
                            conn.commit()

    # wait 1 hour
    print("\n\n==============================\nlooping\n==============================\n\n", flush=True)
    print(f"loop start -- {datetime.now().astimezone(EST)}", flush=True)
    time.sleep(3600)
    # time.sleep(10)
    print("\n\n", flush=True)
