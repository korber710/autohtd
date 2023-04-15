"""
This module works as an API for the Episodate server.

It uses HTTP to reach endpoints exposed by the Episodate server.
"""

import urllib
import requests


class EpisodateAPI:
    """
    EpisodateAPI contains methods to run lookup and search for TV shows on the
    Episodate server to get data related to TV shows, like when they are
    scheduled to come out.
    """

    def __init__(
        self,
        search_base_url: str = "https://www.episodate.com/api/search?",
        lookup_base_url: str = "https://www.episodate.com/api/show-details?",
    ):
        """
        Initializes the EpisoadteAPI object.

        :param search_base_url: The url base for searching TV shows.
        :param lookup_base_url: The url base for looking up TV show details.
        """
        self.search_base_url = search_base_url
        self.lookup_base_url = lookup_base_url

    def search(self, name: str, page: int = None):
        """
        Searches for TV show entries from the Episodate database and returns a
        list of dictionaries containing the show id, show name, country code,
        etc.

        :param name: The name of the TV show to search for.
        :param page: Page number to return from the search, defaults to '1'.
        """
        params = {"q": name}
        if page:
            params["page"] = page
        encoded_params = urllib.parse.urlencode(params)
        search_url = f"{self.search_base_url}{encoded_params}"

        response = requests.get(search_url)

        return response.json()["tv_shows"]

    def lookup(self, identifier: str):
        """
        Gets details related to a TV show.

        :param identifier: The permalink or id of the TV show to search for.
        """
        params = {"q": identifier}
        encoded_params = urllib.parse.urlencode(params)
        lookup_url = f"{self.lookup_base_url}{encoded_params}"

        response = requests.get(lookup_url)

        return response.json()
