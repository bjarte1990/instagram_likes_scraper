from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time
import random
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

URL = 'https://www.instagram.com/p/your-post-comes-here/'
base_url = 'https://www.instagram.com/'

def get_profile_infos(profiles):
    infos = []
    for profile in profiles:
        print('[INFO] Parsing user %s' % profile)
        try:
            html = requests.get(base_url + profile + '/')
            soup = BeautifulSoup(html.text, 'lxml')
            item = soup.select_one("meta[property='og:description']")
            name = item.find_previous_sibling().get("content").split("•")[0]
            info = re.search('(.*) Followers, (.*) Following, (.*) Posts .*', item.get("content"))
            (followers, following, posts)= info.groups()
            name = name.split('(')[0].strip()

            infos.append({'id': profile, 'name': name, 'followers': followers, 'following': following, 'posts': posts})
        except:
            print("[ERROR] Parsing error for user: %s" % profile)
    return infos

def get_liking_profiles(url):

    driver = webdriver.Chrome('./chromedriver')
    driver.get(url)

    likes_a = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div[2]/section[2]/div/div/a')
    driver.execute_script('arguments[0].scrollIntoView();', likes_a)
    like_num = int(likes_a.text.replace(',', '').split()[0])

    likes_a.send_keys(Keys.ENTER)
    time.sleep(2)
    # now the dialog opened

    dialog = driver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div')

    profiles = set()

    # while len(profiles) < like_num:
    for i in range(10):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
        time.sleep(random.randint(500,1000)/1000)
        actual_profiles = driver.find_elements_by_xpath('/html/body/div[3]/div/div[2]/div/div/div')
        profiles = profiles.union(set(map(lambda x: x.text.split('\n')[0], actual_profiles)))


liking_profiles = get_liking_profiles(URL)
profile_infos = get_profile_infos(liking_profiles)


df = pd.DataFrame(profile_infos)
df.to_excel('profiles.xlsx', index=False)