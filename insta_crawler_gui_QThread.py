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

import config_diag

class Crawler(QThread):
    
    log_update = pyqtSignal(str)
    
    def __init__(self, driver, param):
        QThread.__init__(self)
        self.driver = driver
        self.param = param

    def log_append(self, text):
        self.log_update.emit(text)
        #self.text_log.append(text)
        #self.text_log.moveCursor(QTextCursor.End)

    def pq_fy(self, source_html, tag, startswith_str = ''):
        for i in pq(source_html)(tag).items():
            if i.text().strip().startswith(startswith_str):
                return json.loads(i.text()[i.text().find('{'):i.text().rfind('}') + 1])
            
    def get_parsed_urls_and_names_from_node(self, node):
        fn_pre = str(node['taken_at_timestamp']) + "_liked_by_" + str(node['edge_media_preview_like']['count']) + "_"
        r = {}
        for i in self.get_downloadable_url_from_node(node):
            r[i] = fn_pre
        return r

    def get_downloadable_url_from_node(self, node):
        r = []
        if node['is_video']:
            try:
                r.append(node['video_url'])
            except:
                self.log_append('video needs to be downloaded from the subpage')
        else:
            try:
                for i in node['edge_sidecar_to_children']['edges']:
                    #print(i['node']['display_url'])
                    r += self.get_downloadable_url_from_node(i['node'])
                    #r[i['node']['display_url']] = fn_pre
            except:
                r.append(node['display_url'])
        return r
        
    def get_end_cursor_from_page_info(self, page_info):
        if page_info['has_next_page']:
            return page_info['end_cursor']
        return False

    def download_from_dic(self, dic, dl_path):
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',}
        all_dup = True
        if not os.path.exists(dl_path):
            os.makedirs(dl_path)
        for i in dic:
            if not self.param['running']: return True
            path_fn = dl_path + dic[i] + self.parse_file_name(i)
            if glob.glob(dl_path + '*' + self.parse_file_name(i)):#os.path.exists(path_fn):
                self.log_append(path_fn + ' exists.')
                continue
            with open(path_fn, 'wb') as f:
                f.write(requests.get(i, headers).content)
            time.sleep(2 + random.randint(1, 800) / 300)
            self.log_append('downloading ' + path_fn)
            all_dup = False
        return all_dup

    def get_ness_info(self, link):
        self.log_append('crawling ' + link)
        driver.get(link)
        b = self.pq_fy(driver.page_source, 'script[type="text/javascript"]', 'window._sharedData = ')
        ins_id = b['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        parsed_path = param["path"] + self.parse_instagram_er(link) + '/'
        return ins_id, parsed_path, b
        
    def download_first_page(self, link, end_cursor = False):
        ins_id, parsed_path, b = self.get_ness_info(link)    
        dl_link = {}
        if end_cursor:
            self.download_from_query(ins_id, end_cursor, parsed_path, link)
            return
        for i in b['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']:
            dl_link.update(self.get_parsed_urls_and_names_from_node(i['node']))
        end_cursor = self.get_end_cursor_from_page_info(b['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['page_info'])
        if self.download_from_dic(dl_link, parsed_path) and not param["ignore_downloaded_and_loop"]:
            self.log_append('encountered duplicates; to continue, enable dup continue')
            return
        self.download_from_query(ins_id, end_cursor, parsed_path, link)
            
    def download_from_query(self, ins_id, end_cursor, parsed_path, link):
        while end_cursor:
            if not self.param['running']: return
            time.sleep(2 + random.randint(1, 800) / 300)
            next_query = param["query_format"].format(ins_id=ins_id, end_cursor=end_cursor)
            self.log_append('next query:')
            self.log_append(link)
            self.log_append(end_cursor)
            self.log_append(next_query)
            driver.get(next_query)
            graphql_query = driver.find_element_by_tag_name("pre").text
            graphql_hasbin = json.loads(graphql_query)
            dl_link = {}
            end_cursor = self.get_end_cursor_from_page_info(graphql_hasbin['data']['user']['edge_owner_to_timeline_media']['page_info'])
            for i in graphql_hasbin['data']['user']['edge_owner_to_timeline_media']['edges']:
                #print(i['node'])
                dl_link.update(self.get_parsed_urls_and_names_from_node(i['node']))
            if self.download_from_dic(dl_link, parsed_path) and not param["ignore_downloaded_and_loop"]:
                self.log_append('encountered duplicates; to continue, enable dup continue')
                return
        self.log_append('completed crawling ' + link)
            
    def parse_file_name(self, link):
        a = link[link.find('.com') + 5 : link.find("?")]
        return a[a.rfind('/') + 1:]

    def parse_instagram_er(self, link):
        return link[link.find('.com/') + 5 : max(link.rfind('?') - 1, link.rfind('/'))]

    def login(self, brawser):
        usr_name = self.param['usr_name']
        pswd = self.param['pswd']
        brawser.get('https://www.instagram.com/accounts/login/')
        time.sleep(1)
        try:
            self.log_append("loggging in with usr name " + usr_name + '...')
            brawser.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input').send_keys(usr_name)
            time.sleep(0.2)
            brawser.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input').send_keys(pswd)
            time.sleep(0.5)
            brawser.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]').click()
            time.sleep(1)
            return True
        except:
            self.log_append("try again:(")
            return False

    def crawling(self):
        if len(self.param["dl_from_end_cursor"][1]) > 0:
            self.download_first_page(self.param["dl_from_end_cursor"][0], self.param["dl_from_end_cursor"][1])
        elif len(self.param["dl_from_end_cursor"][0]) > 0:
            self.download_first_page(self.param["dl_from_end_cursor"][0])
        else:
            for i in self.param["ins_model"]:
                try:
                    time.sleep(2)
                    self.download_first_page(i)
                except:
                    self.log_append("failed crawling " + i)
        self.log_append('jobs done')

    def run(self):
        self.log_append('gogogadget')
        if not self.param['logged_in']:
            self.param['logged_in'] = self.login(self.driver)
        if not self.param['logged_in']: return
        self.log_append('phew, login successful')
        self.crawling()



class insta_crawler_Ui(QtWidgets.QMainWindow):

    def load_param(self):
        r = self.text_scrap_links.toPlainText()
        if r[len(r) - 1] != '\n': r += '\n'
        param["ins_model"] = self.string2array(r)
        param['ignore_downloaded_and_loop'] = self.check_dup_continue.isChecked()
        #if len(self.line_scrap_ind_link.text()) > 0 and len(self.line_scrap_ind_token.text()) > 0:
        param["dl_from_end_cursor"] = [self.line_scrap_ind_link.text(), self.line_scrap_ind_token.text()]

    def click_scrawl(self):
        self.load_param()
        if self.param['running']:
            self.stalp_running()
        else:
            self.start_running()
        #return False        
        
    def pop_config_window(self):
        self.config_window = config_diag.Query_URL_Ui(self.param)

    def array2string(self, array, sepchar = '\n'):
        r = ''
        for i in array: r += i + sepchar
        return r

    def string2array(self, string, sepchar = '\n'):
        r = []
        while sepchar in string:
            r += [string[0:string.index(sepchar)]]
            string = string[string.index(sepchar) + 1:]
        return r

    def __init__(self, driver, param):
        super(insta_crawler_Ui, self).__init__()
        uic.loadUi('isnta_scrapper_qtdesign.ui', self)
        self.driver                 = driver
        self.param                  = param
        self.param['logged_in']     = False
        self.param['running']       = False
#        self. = self.findChild(QtWidgets., '') # Find the button
        self.button_scrap           = self.findChild(QtWidgets.QPushButton, 'scrap_button') # Find the button
        self.button_scrap.clicked.connect(self.click_scrawl)
        self.text_scrap_links       = self.findChild(QtWidgets.QTextEdit, 'scrap_links') # Find the button
        self.line_scrap_ind_link    = self.findChild(QtWidgets.QLineEdit, 'scrap_ind_link') # Find the button
        self.line_scrap_ind_token   = self.findChild(QtWidgets.QLineEdit, 'scrap_ind_token') # Find the button
        self.text_log               = self.findChild(QtWidgets.QTextEdit, 'log') # Find the button

        self.action_query_URL       = self.findChild(QtWidgets.QAction, 'actionSet_Query_URL') # Find the button
        self.action_query_URL.triggered.connect(self.pop_config_window)
        self.action_debug       = self.findChild(QtWidgets.QAction, 'actionDebug') # Find the button
        self.action_debug.triggered.connect(self.debug)

        self.check_dup_continue     = self.findChild(QtWidgets.QCheckBox, 'checkBox') # Find the button
        self.check_works            = self.findChild(QtWidgets.QCheckBox, 'works_check') # Find the button
        self.check_works.stateChanged.connect(self.draw_bkgrnd)
        self.text_scrap_links.setText(self.array2string(self.param['ins_model'])) 

        self.check_dup_continue.setChecked(self.param["ignore_downloaded_and_loop"])
        self.crawler = Crawler(self.driver, self.param)
        self.crawler.finished.connect(self.finished)
        self.crawler.log_update.connect(self.update_log)

        self.draw_bkgrnd()
        self.show()
        #self.crawler.terminated.connect(self.finished)

    def debug(self):
        self.check_works.setChecked(False)

    def update_log(self, text):
        self.text_log.append(text)
        self.text_log.moveCursor(QTextCursor.End)

    def resizeEvent(self,event):
        #print('poo')
        if not self.param['running']:
            self.draw_bkgrnd()


    def finished(self):
        self.param['running'] = False
        self.button_scrap.setText('scrap')
        self.draw_bkgrnd()

    def stalp_running(self):
        # if self.crawler.isRunning():
        #     self.crawler.terminate()
        self.finished()
        self.text_log.append('stop signal sent, wait for failed crawling message...')

    def draw_bkgrnd(self):
        if not self.check_works.isChecked():
            self.text_log.setStyleSheet("background-image: url(works_on_mine.png); background-repeat: no-repeat; background-position: center; background-color: rgba(255, 255, 255, 10); background-attachment: fixed")
        else:
            self.text_log.setStyleSheet("background-image: url()")

    def start_running(self):
        self.param['running'] = True
        self.text_log.append('crawling started')
        self.button_scrap.setText('stalp')
        self.text_log.setStyleSheet("background-image: url()")
        self.crawler.start()

    def closeEvent(self, event):
        self.driver.quit()
        self.load_param()
        self.stalp_running()

def load_param():
    param["path"] = "./ins/"
    param["ignore_downloaded_and_loop"] = False
    param["ins_model"] = ['https://www.instagram.com/enakorin/']
    param["dl_from_end_cursor"] = []#webpage, end_cursor
    param["query_format"] = 'https://www.instagram.com/graphql/query/?query_hash=44efc15d3c13342d02df0b5a9fa3d33f&variables=%7B%22id%22%3A%22{ins_id}%22%2C%22first%22%3A12%2C%22after%22%3A%22{end_cursor}%22%7D'
    param['param_loc'] = 'instagram.json'
    param['usr_name'] = 'whatwhat'
    param['pswd'] = 'inthebutt'
    param['logged_in'] = False
    param['running'] = False

    #load param from file:
    paramR = {}
    if os.path.exists(param['param_loc']):
        with open(param['param_loc']) as json_file:
            paramR = json.load(json_file)
    for i in paramR.keys():
        param[i] = paramR[i]

def save_param():
    param["dl_from_end_cursor"] = []
    with open(param['param_loc'], 'w') as outfile:
        json.dump(param, outfile)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    param = {}
    driver = webdriver.Chrome()
    load_param()
    wind = insta_crawler_Ui(driver, param)
    app.exec_()
    print('savin\' param....')
    save_param()
