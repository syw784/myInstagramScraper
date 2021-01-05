# myInstagramScraper
yeah i wrote my own instagram scraper despite there are 10k of them on github, fml


1. HOW to use?
this thing uses selenium + chrome's webdriver because I dont understand headings, so 1. you need google chrome; 2. you need google chrome webdriver @ https://chromedriver.chromium.org/downloads. be ware that the chrome ver and webdriver ver must match, otherwise it will cause issues, which is why i dont like selenium that much.

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
check the options-config to put in the necessary info: 
