import pandas as pd
import numpy as np
import re
import time

# row 생략 없이 출력
pd.set_option('display.max_rows', None)
# col 생략 없이 출력
pd.set_option('display.max_columns', None)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def remove_numbers(text):
  return re.sub(r'\d+', '', text)
def remove_string(text):
  p = re.compile('[a-zA-Z]+')
  m = p.search(text)
  if m:
    text = ''
  return text
def remove_pa(li):
  li = list(filter(None, li))

def remove_pa_from(li):
    lis = []
    for i in li:
        p = re.compile('(\d+)\((\d+)\)')
        s = p.search(i)
        if s:
           text1 = s.group(1)
           text2 = s.group(2)
           lis += text1, text2
        else:
           lis.append(i)
    return lis


def prepro(pla1):
  remove_set = {' '}          
  player1 = pla1.get_attribute('textContent')
  player1 = list(player1.split('\n'))
  player1 = [re.sub(('\\t|/|/s'),'',i) for i in player1]
  player1 = list(filter(None, player1))
  player1 = [i for i in player1 if i not in remove_set]
  return player1


webdriver_service = Service()
driver = webdriver.Chrome(service = webdriver_service, options = options)


Econ_DF = pd.DataFrame()

pages = range(4,5)
for page in pages:
    driver.get(f'https://www.vlr.gg/matches/results/?page={page}')
    time.sleep(1)

    index_match=5
    match = driver.find_elements(By.XPATH,f'//*[@id="wrapper"]/div[{3}]/div/div/a')
    print(f'{page} Page')

    while True:
        if index_match == 11: #len(match)
            break

        print('Match : ',index_match+1,'/',len(match))
        link = match[index_match].get_attribute("href")
        driver.execute_script('window.open("");')
        driver.switch_to.window(driver.window_handles[-1])
        link = link+'/?game=all&tab=economy'
        driver.get(link)
        
        #WebDriverWait(driver, 30).until(EC.presence_of_element_located(By.XPATH, '//*[@id="wrapper"]/div[3]/div[3]/div[1]/div[1]/div[1]/a/div/div[1]'))
        time.sleep(1)

        cur_url = driver.current_url
        #print(cur_url)


        for i in range(1,7):
          try:
            dgi = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[3]/div[3]/div[7]/div/div[3]/div[{i}]')
            ele = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[3]/div[3]/div[7]/div/div[3]/div[{i}]/div[1]')

            if dgi.get_attribute('data-game-id') == 'all':
              continue
          except:
            print(i)
            continue

          data_game_id = dgi.get_attribute('data-game-id')
          print(data_game_id)

          eco = prepro(ele)[5:]
          if eco == []:
            continue
          else:
             eco = remove_pa_from(eco)

          econ_df = pd.DataFrame((np.array(eco)).reshape(2,10),columns = ['Team','Pistol','Eco','Eco won','Semi_eco','Semi_eco won','Semi_buy','Semi_buy won','Full_buy','Full_buy won'])
          econ_df['data_game_id'] = data_game_id
          print(econ_df)
          Econ_DF = pd.concat([Econ_DF,econ_df],ignore_index=True)
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(1)

        index_match += 1

Econ_DF.to_csv('C:/Users/WTA/crawler/Econ.csv',index=False)