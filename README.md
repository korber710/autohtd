# Steve Korber's Automated Home Torrent Downloader

This project was developed as a home project but can be setup be utilized on any
home setup with a simple Linux machine.

## Usage

Navigate to the IP of your server (typically set a static IP in your router) X.X.X.X:80 on a webbrowser on any device on the same local network.
Select the TV or Movie tab and search for a movie or show. For TV you will need to select the season. 
After, click the Add button to push the show/movie to the database.
The scheduler will pickup the show on its next loop and download what you added and transfer it to your defined local harddrive.

## Prerequisites

This project requires the following to work:
* Jenkins server (can be running locally) with the target machine as an agent
* PostgreSQL server that can be accessed from the target machine
* qBittorrent installed on the target machine
* Docker installed on the target machine

## Setup

WIP