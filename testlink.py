import aiohttp
import urllib
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import csv
import urllib
import sys
import re
import random
import os

#webbrowser.open("https://cdn.discordapp.com/attachments/696433109163573248/703624158688313404/20200425_170951.jpg")


url = "https://cdn.discordapp.com/attachments/696433109163573249/703642551269457940/D31PKpsWsAIN9aA.jpg"


url_filename = url.split('/')[-1]

print(url_filename)

urllib.request.urlretrieve(url, "pog.jpg")