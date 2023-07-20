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
  return li

def prepro(pla1):
  remove_set = {' '}          
  player1 = pla1.get_attribute('textContent')
  player1 = list(player1.split('\n'))
  player1 = [re.sub(('\\t|/|/s'),'',i) for i in player1]
  player1 = list(filter(None, player1))
  player1 = [i for i in player1 if i not in remove_set]
  return player1

def prepro2(pla1):
  remove_set = {' '}          
  player1 = pla1.get_attribute('textContent')
  player1 = list(player1.split('\n'))
  player1 = [re.sub(('\\t|/|/s'),'',i) for i in player1]
  #player1 = list(filter(None, player1))
  #player1 = [i for i in player1 if i not in remove_set]
  return player1

webdriver_service = Service()
driver = webdriver.Chrome(service = webdriver_service, options = options)

Perform_DF = pd.DataFrame()

pages = range(4,100)
for page in pages:
    driver.get(f'https://www.vlr.gg/matches/results/?page={page}')
    time.sleep(1)

    index_match=0
    match = driver.find_elements(By.XPATH,f'//*[@id="wrapper"]/div[{3}]/div/div/a')
    print(f'{page} Page')

    while True:
        if index_match == len(match):
            break

        print('Match : ',index_match+1,'/',len(match))
        link = match[index_match].get_attribute("href")
        driver.execute_script('window.open("");')
        driver.switch_to.window(driver.window_handles[-1])
        link = link+'/?game=all&tab=performance'
        driver.get(link)
        
        #WebDriverWait(driver, 30).until(EC.presence_of_element_located(By.XPATH, '//*[@id="wrapper"]/div[3]/div[3]/div[1]/div[1]/div[1]/a/div/div[1]'))
        time.sleep(0.5)

        cur_url = driver.current_url
        print(cur_url)

        
        for i in range(1,7):
          try:
            dgi = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[3]/div[3]/div[7]/div/div[3]/div[{i}]')
            ele = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[3]/div[3]/div[7]/div/div[3]/div[{i}]/div[1]/table[3]')
            print(i, 'Complete')

            if dgi.get_attribute('data-game-id') == 'all':
              print('all')
              continue
          except:
            print(i, 'None')
            continue

          try:
            data_game_id = dgi.get_attribute('data-game-id')
            print(data_game_id)
            
            player1 = []
            player2 = []
            for j in range(2,7):
              pla1 = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[3]/div[3]/div[7]/div/div[3]/div[{i}]/div[1]/table[3]/tbody/tr[{j}]/td[1]/div/div')
              pla2 = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[3]/div[3]/div[7]/div/div[3]/div[{i}]/div[1]/table[3]/tbody/tr[1]/td[{j}]/div/div')
              name1 = prepro(pla1)
              name2 = prepro(pla2)

              kill1_sum = 0
              kill2_sum = 0
              for k in range(2,7):
                
                op_kill1 = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[3]/div[3]/div[7]/div/div[3]/div[4]/div[1]/table[3]/tbody/tr[{j}]/td[{k}]/div/div[1]')
                op_kill2 = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[3]/div[3]/div[7]/div/div[3]/div[4]/div[1]/table[3]/tbody/tr[{k}]/td[{j}]/div/div[2]')
                op_kill1 = prepro(op_kill1); op_kill2 = prepro(op_kill2)
                if ''.join(op_kill1)=='':
                  kill1_sum += 0
                else:  
                  kill1_sum = int(''.join(op_kill1)) + kill1_sum
                if ''.join(op_kill2)=='':
                  kill2_sum += 0
                else:  
                  kill2_sum = int(''.join(op_kill2)) + kill2_sum

              name1.append(kill1_sum)
              name2.append(kill2_sum)
              player1.append(name1)
              player2.append(name2)

            player1 = pd.DataFrame(np.array(player1),columns=['Player','Team','Op_kill'])
            player2 = pd.DataFrame(np.array(player2),columns=['Player','Team','Op_kill'])
            player_df = pd.concat([player1,player2],ignore_index=True)


            perform = []
            perform_df = pd.DataFrame()
            for j in range(2,12):
              pla = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[3]/div[3]/div[7]/div/div[3]/div[{i}]/div[2]/table/tbody/tr[{j}]/td[1]/div/div')
              name = prepro(pla)

              for k in range(3,15):
                stat_sq = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[3]/div[3]/div[7]/div/div[3]/div[{i}]/div[2]/table/tbody/tr[{j}]/td[{k}]/div')
                stats = prepro2(stat_sq)
                if stats == ['','','']:
                  name += '0'
                else:
                  name += remove_pa([remove_string(i) for i in stats])

              perform.append(name)
            perform = pd.DataFrame(np.array(perform),columns = ['Player','Team','2K','3K','4K','5K','1v1','1v2','1v3','1v4','1v5','ECON','PL','DE'])

            perform_df = pd.merge(player_df,perform,on=['Player','Team'])
            perform_df['data_game_id'] = data_game_id
            Perform_DF = pd.concat([Perform_DF,perform_df],ignore_index=True)

          except:
            continue
    
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(0.5)

        index_match += 1

Perform_DF.to_csv('C:/Users/WTA/crawler/Perform.csv',index=False)