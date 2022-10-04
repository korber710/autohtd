############################################################
#
#   Auto Home Torrent Downloader Back-end Server App
#   created by Steve Korber
#   korbersa@outlook.com
#
############################################################

# import
import time
from flask import Flask, request, jsonify
import sys
import pytz
import psycopg2
import os
import json
import difflib
from flask_cors import CORS
import argparse

# import custom libs
from yts_library.yts_library import YTSController
from episodate_library.episodate_library import *

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--host-ip', help='The IP used for the torrent client and the PostgreSQL server')
parser.add_argument('--db-secret', help='PostgreSQL username:password')
parser.add_argument('--hdd-path', help='Comma seperated path to HDD (eg. media,ubuntu,Seagate Expansion Drive1)')
args = parser.parse_args()

# constants
EST = pytz.timezone("US/Eastern")
GMT = pytz.timezone("GMT")
HOST_IP = args.host_ip
POSTGRES_USER = args.db_secret.split(":")[0]
POSTGRES_PASSWORD = args.db_secret.split(":")[1]
HDD_BASE_PATH = args.hdd_path
RETURN_OBJ = {"result": -1, "description": "", "data": {}}

# create flask app with CORS
app = Flask(__name__)
CORS(app)                          
                                                
@app.route('/')                                 
def index():                                    
  return "Hello, world. Test!", 200             
                                                
@app.route('/api/v1/tv/search', methods=["POST"])
def tvSearchV1():                               
    """TV Search endpoint, used to lookup shows that exist in the TV API and 
    finds the best match for the user.                
    """                                         
    # setup return object                       
    return_obj = RETURN_OBJ                     
                                                
    # try to get the body from the payload and parse it
    try:                                        
        body = request.get_json(force=True)
        print(body, file=sys.stderr, flush=True)
        searched_name = body["name"]
    except Exception as exc:                    
        print(f"{type(exc).__name__} error occurred - {exc}", file=sys.stderr, flush=True)
        return_obj["result"] = -1               
        return_obj["description"] = "tvSearchV1:: failed to parse incoming data"
        print(return_obj, file=sys.stderr, flush=True)
        return jsonify(return_obj), 500         
                                                
    # create a new tv search controller         
    try:                                        
        tv_search_obj = TVSearchController()    
    except Exception as exc:
        print(f"{type(exc).__name__} error occurred - {exc}", file=sys.stderr, flush=True)
        return_obj["result"] = -1
        return_obj["description"] = "tvSearchV1:: tv database error"
        print(return_obj, file=sys.stderr, flush=True)
        return jsonify(return_obj), 500
    
    # get the results from the given name
    results = tv_search_obj.search(searched_name)
    show_obj = results["data"]
    show_list = []

    # try to parse the shows from Canada or US first 
    # then get the closest match to the user input
    try:
        print(show_obj["tv_shows"], file=sys.stderr, flush=True)
        for show in show_obj["tv_shows"]:
            if show["country"] in ["CA", "US"]:
                show_list.append(show["name"])
            else:
                show_list.append("")
        print(show_list, file=sys.stderr, flush=True)
        best_show = difflib.get_close_matches(searched_name, show_list)[0]
    except Exception as exc:
        print(f"{type(exc).__name__} error occurred - {exc}", file=sys.stderr, flush=True)
        return_obj["result"] = -1
        return_obj["description"] = "tvSearchV1:: show not found"
        print(return_obj, file=sys.stderr, flush=True)
        return jsonify(return_obj), 500
    
    # get the number of seasosn available from the best show
    try:
        show_index = show_list.index(best_show)
        results = tv_search_obj.lookup(show_obj["tv_shows"][show_index]["id"])
        show_details = results["data"]["tvShow"]
        season_list = get_season_numbers(show_details)

        return_obj["data"] = {}
        return_obj["data"]["name"] = best_show
        return_obj["data"]["seasons"] = season_list[-1]
    except Exception as exc:
        print(f"{type(exc).__name__} error occurred - {exc}", file=sys.stderr, flush=True)
        return_obj["result"] = -1
        return_obj["description"] = "tvSearchV1:: error getting show id"
        print(return_obj, file=sys.stderr, flush=True)
        return jsonify(return_obj), 500
    
    # return successful with the best show in the data key
    return_obj["result"] = 0
    return_obj["description"] = "tvSearchV1 successful"
    print(return_obj, file=sys.stderr, flush=True)
    return jsonify(return_obj), 200

@app.route('/api/v1/tv/add', methods=["POST"])
def tvAddV1():
    """
    inputs:
    "name" - str - show name
    "season" - int - season number
    "current" - list - list of episodesID already downlaoded (can be empty)
    """
    return_obj = {
        "result": -1,
        "description": "",
        "data": ""
    }
    conn = psycopg2.connect(user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=HOST_IP, port="5432", database="home")
    cur = conn.cursor()
    try:
        body = request.get_json(force=True)
        print(body, file=sys.stderr, flush=True)
    except Exception as exc:
        print(f"{type(exc).__name__} error occurred - {exc}", file=sys.stderr, flush=True)
        return_obj["result"] = -1
        return_obj["description"] = "tvAddV1:: failed to parse incoming data"
        print(return_obj, file=sys.stderr, flush=True)
        return jsonify(return_obj), 500
    
    parentDir = os.path.join(os.sep, *HDD_BASE_PATH.split(","), "TV Shows")
    try:
      showName = body["name"].replace(":", "")
      seasonName = "Season {}".format(body['season'])
      showDir = os.path.join(parentDir, showName, seasonName)
      if not os.path.exists(showDir):
          os.makedirs(showDir, exist_ok=True)
          time.sleep(1)
      if not os.path.exists(showDir):
          return_obj["result"] = -1
          return_obj["description"] = "tvAddV1:: couldn't create dir"
          print(return_obj, file=sys.stderr, flush=True)
          return jsonify(return_obj), 500
      rawDir = f"{HDD_BASE_PATH},TV Shows,{showName},{seasonName}"
      if len(body["current"]) == 0:
          data = {"episodes": body["current"]}
      else:
          data = {"episodes": []}
          for episodeID in body["current"]:
              data["episodes"].append({"episodeID": episodeID, "torrentID": "", "completed": True})
      cur.execute("INSERT INTO public.tv_shows VALUES (default, '{}', {}, '{}', '{}')".format(showName.replace("'", "''"), body['season'], rawDir, json.dumps(data)))
      updatedRows = cur.rowcount
      print("updated rows {}".format(updatedRows))
      conn.commit()
    except Exception as exc:
        print(f"{type(exc).__name__} error occurred - {exc}", file=sys.stderr, flush=True)
        return_obj["result"] = -1
        return_obj["description"] = "tvAddV1:: failed"
        print(return_obj, file=sys.stderr, flush=True)
        return jsonify(return_obj), 500
    return_obj["result"] = 0
    return_obj["description"] = "tvAddV1 successful"
    print(return_obj, file=sys.stderr, flush=True)
    return jsonify(return_obj), 200

@app.route('/api/v1/movie/search', methods=["POST"])
def movieSearchV1():
    """
    inputs:
    "name" - str - show name
    """
    return_obj = {
        "result": -1,
        "description": "",
        "data": ""
    }
    try:
        body = request.get_json(force=True)
        print(body, file=sys.stderr)
    except Exception as exc:
        print(f"{type(exc).__name__} error occurred - {exc}", file=sys.stderr, flush=True)
        return_obj["result"] = -1
        return_obj["description"] = "movieSearchV1:: failed to parse incoming data"
        return jsonify(return_obj), 500
    try:
        ytsObj = YTSController()
    except Exception as exc:
        print(f"{type(exc).__name__} error occurred - {exc}", file=sys.stderr, flush=True)
        return_obj["result"] = -1
        return_obj["description"] = "movieSearchV1:: yts controller error"
        return jsonify(return_obj), 500
    results = ytsObj.searchAll(body["name"])
    if results["result"] != 0:
      return_obj["result"] = -1
      return_obj["description"] = "movieSearchV1:: no movies"
      return jsonify(return_obj), 500
    return_obj["data"] = results
    return_obj["result"] = 0
    return_obj["description"] = "movieSearchV1 successful"
    return jsonify(return_obj), 200

@app.route('/api/v1/movie/add', methods=["POST"])
def movieAddV1():
    """
    inputs:
    "name" - str - movie name
    """
    return_obj = {
        "result": -1,
        "description": "",
        "data": ""
    }
    conn = psycopg2.connect(user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=HOST_IP, port="5432", database="home")
    cur = conn.cursor()
    try:
        body = request.get_json(force=True)
        print(body, file=sys.stderr)
    except Exception as exc:
        print(f"{type(exc).__name__} error occurred - {exc}", file=sys.stderr, flush=True)
        return_obj["result"] = -1
        return_obj["description"] = "movieAddV1:: failed to parse incoming data"
        return jsonify(return_obj), 500
    try:
      parentDir = f"{HDD_BASE_PATH},Movies"
      movieName = body["name"].replace(":", "")
      cur.execute("INSERT INTO public.movies VALUES (default, '{}', '{}', null)".format(movieName.replace("'", "''"), parentDir))
      updatedRows = cur.rowcount
      print("updated rows {}".format(updatedRows))
      conn.commit()
    except Exception as exc:
        print(f"{type(exc).__name__} error occurred - {exc}", file=sys.stderr, flush=True)
        return_obj["result"] = -1
        return_obj["description"] = "movieAddV1:: failed"
        return jsonify(return_obj), 500
    return_obj["result"] = 0
    return_obj["description"] = "movieAddV1 successful"
    return jsonify(return_obj), 200

if __name__ == "__main__":
  app.run("0.0.0.0")
