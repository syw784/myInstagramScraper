# myInstagramScraper
mom look another creep wrote a thing to scrape instagram just like many other creeps on github

1. HOW to use?
this thing uses selenium + chrome's webdriver because I dont understand headings to use request, so 1. you need google chrome; 2. you need google chrome webdriver @ https://chromedriver.chromium.org/downloads. be ware that the chrome ver and webdriver ver must match, otherwise it will cause issues, which is why i dont like selenium that much.

2. 
once  webdriver.exe is downloaded in this folder, run insta_crawler_gui_QThread.py. it uses all these junk:
from PyQt5 import QtWidgets, uic
import sys
from functools import partial
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor

from selenium import webdriver
import os
import json
import time
import random
import requests
import glob
from pyquery import PyQuery as pq
import threading

so pip install whatever you dont have.

3.
the main GUI looks like:


![Chungus](https://github.com/syw784/myInstagramScraper/raw/main/lol/1.PNG)

make sure to go to options-coinfig and put in your user name and password. dont change other crap, these are sophisticatedly reverse engineered through front, back and mid end magic and contracted with js demon to give these unholy strings.

put instagram links in scrap linkz, and press scrape.

press stalp to stop.
