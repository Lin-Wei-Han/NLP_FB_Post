from selenium import webdriver
from fake_useragent import UserAgent
from dotenv import load_dotenv, find_dotenv
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re

chrome_options = webdriver.ChromeOptions()

# 允許所有網站通知行為
chrome_options.add_experimental_option(
    "prefs", 
    {
        "profile.default_content_setting_values.notifications": 1
    }
)

#ua = UserAgent()
#random_user_agent = ua.random
#chrome_options.add_argument(f"user-agent={random_user_agent}")


load_dotenv(find_dotenv())

facebook_mail = os.environ.get("FACEBOOK_MAIL")
facebook_password = os.environ.get("FACEBOOK_PASSWORD")


# 啟動 webdriver 並登入 FB


driver = webdriver.Chrome(options = chrome_options)

# 設定視窗大小
driver.set_window_size(800, 800)

# Facebook 登入
login_url = 'https://www.facebook.com/login/device-based/regular/login/?login_attempt=1&next=https%3A%2F%2Fwww.facebook.com'
driver.get(login_url)

email_element = driver.find_element(By.CSS_SELECTOR,'#email_container input')
password_element = driver.find_element(By.CSS_SELECTOR,'._55r1._1kbt input')

email_element.send_keys(facebook_mail)
password_element.send_keys(facebook_password)

login_button = driver.find_element(By.CSS_SELECTOR, '#loginbutton')
login_button.click()

time.sleep(3)

# 前往指定社團頁面
url = 'https://www.facebook.com/groups/traveler168'

driver.get(url)

# time.sleep(600)
js_script =  '''
    let elements = document.querySelectorAll(".x9f619.x1n2onr6.x1ja2u2z.x1s85apg[hidden]");
    for (let element of elements) {
        let parentElement = element.closest(".x1yztbdb.x1n2onr6.xh8yej3.x1ja2u2z");
        parentElement.parentNode.removeChild(parentElement);
    }
'''

def getElement(driver):
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    elements = soup.select('.x1yztbdb.x1n2onr6.xh8yej3.x1ja2u2z')
    return elements

def getPostData(elements):
    name_list, like_list, date_list, link_list, article_list = [], [], [], [], []
    for element in elements:
        try:
            name = element.select('.xt0psk2 span')[0].text
            name_list.append(name)
        except:
            continue

        try:
            like = element.select('.xrbpyxo.x6ikm8r.x10wlt62.xlyipyv.x1exxlbk span.x1e558r4')[0].text
            like_list.append(like)
        except:
            like_list.append(0)

        try:
            date_time = element.select('.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.x1heor9g.xt0b8zv.xo1l8bm span')[0].text
            date_list.append(date_time)
        except:
            date_list.append('')

        try:
            link = element.select('.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.x1sur9pj.xkrqix3.xi81zsa.xo1l8bm')[0].get('href')
            base_url = re.match(r"(https://www\.facebook\.com/groups/traveler168/posts/\d+)", link)
            if base_url:
                link_list.append(base_url.group(1))
            else:
                link_list.append(link)
        except:
            link_list.append('')

        try:
            article = element.select_one('.x1iorvi4.x1pi30zi.x1l90r2v.x1swvt13').get_text()
            article_list.append(article)
        except:
            article_list.append('')

    df = pd.DataFrame({
        '作者': name_list,
        '讚數': like_list,
        '時間': date_list,
        '連結': link_list,
        '貼文內容': article_list
    })
    return df


def convert_time_to_date(time_str):
    today = datetime.now()
    if '小時' in time_str or '分鐘' in time_str:
        hours_ago = int(re.findall(r'\d+', time_str)[0])
        target_date = today - timedelta(hours = hours_ago)
    elif '天' in time_str:
        days_ago = int(re.findall(r'\d+', time_str)[0])
        target_date = today - timedelta(days = days_ago)
    elif '月' in time_str:
        # Assuming the format is '4月17日下午7:55', only extract month and day
        month, day = map(int, re.findall(r'\d+', time_str[:time_str.index('日') + 1]))
        target_date = datetime(year = 2024, month = month, day = day)
    else:
        return time_str

    return target_date.strftime('2024-%m-%d')


from tqdm import tqdm
import time

data_capacity = 30

# 初始化 tqdm 的進度條
pbar = tqdm(total = data_capacity)

result_df = pd.DataFrame()

amount = 0
while amount < data_capacity:
    
    counter = 0
    while counter <= 3:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.3)
        counter += 1

    try:
        target_class = '.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.x1sur9pj.xkrqix3.xzsf02u.x1s688f'
        targets = driver.find_elements(By.CSS_SELECTOR, target_class)
        for target in targets:
            try:
                if "查看更多" in target.get_attribute('textContent'):
                    target.click()
                    time.sleep(0.3)
            except:
                continue
    except Exception as e:
        print(e)
        pass
    
    elements = getElement(driver)
    post_df = getPostData(elements)

    result_df = pd.concat([result_df, post_df])

    time.sleep(0.3)

    driver.execute_script(js_script)

    result_df['貼文內容'] = result_df['貼文內容'].astype(str)
    amount = len(result_df[~result_df['貼文內容'].str.contains('查看更多')]['連結'].unique())

    # 更新進度條至新的完成數量
    pbar.update(amount - pbar.n)

pbar.close()  
driver.close()



dataset = result_df[~result_df['貼文內容'].str.contains('查看更多')]
dataset = dataset.drop_duplicates(subset = '連結').reset_index(drop = True)
dataset['時間'] = dataset['時間'].apply(convert_time_to_date)


dataset.to_csv('fb_post_02.csv', index = False)
print(dataset)