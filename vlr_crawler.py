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

webdriver_service = Service()
driver = webdriver.Chrome(service = webdriver_service, options = options)

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

def match_data(x):
  ##### Match 정보 #####
  date = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[{x}]/div[3]/div[1]/div[1]/div[2]/div/div[1]')
  hour = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[{x}]/div[3]/div[1]/div[1]/div[2]/div/div[2]')
  Date = date.text+' '+hour.text

  league = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[{x}]/div[3]/div[1]/div[1]/div[1]/a/div/div[1]')
  League = league.text
  stage = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[{x}]/div[3]/div[1]/div[1]/div[1]/a/div/div[2]')
  Stage = stage.text
  patch = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[{x}]/div[3]/div[1]/div[1]/div[2]/div/div[3]/div')
  Patch = remove_string(patch.text)
  bo = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[{x}]/div[3]/div[1]/div[2]/div/div[3]')
  BO = bo.text

  playing_match1 = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[{x}]/div[3]/div[1]/div[2]/div/div[2]/div[1]/span[1]')
  playing_match2 = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[{x}]/div[3]/div[1]/div[2]/div/div[2]/div[1]/span[3]')
  Playing_Match = int(playing_match1.text) + int(playing_match2.text)

  print('Match Data:  ',Date,League,Stage,Patch,BO, Playing_Match)

  M_Data_li = [Date,League,Stage,Patch,BO, Playing_Match]
  return M_Data_li

def TCT(ele):
  tct = ele.get_attribute('outerHTML')
  p = re.compile('class="mod-ct">\d</span>')
  q = re.compile('class="mod-t">\d</span>')
  index1 = 0; index2 = 0
  for item in tct.split()[:40]:
    if p.match(item):
      index1 = tct.split().index(item)
    elif q.match(item):
      index2 = tct.split().index(item)

  if index1 < index2:
    return 'CT'
  else:
    return 'T'
  
def Conti(conti,round):
    conti_score = 0
    for i in range(round-4):
        mat = conti[i:i+4]
        m = re.match('1111',mat)
        if m:
            conti_score += 1
    return conti_score

def Conti_score(score,round):
  sam = [i.split('-') for i in score]
  conti1 = ''.join([str(int(sam[i+1][0])-int(sam[i][0])) for i in range(round-1)])
  conti2 = ''.join([str(int(sam[i+1][1])-int(sam[i][1])) for i in range(round-1)])
  return [Conti(conti1,round),Conti(conti2,round)]

def overview(li,ele):
  try:
    int(li[4])
    num = 14
    round = int(li[0])+int(li[num-3])
    df =li[:num]
    map = df[5]
    result1 = df[0]; result2 = df[-3]
    extended_round1 = int(df[4])
    extended_round2 = int(df[-4])
    map_time = df[6]
    first_half1 = df[2]; second_half1 = df[3]
    first_half2 = df[-6]; second_half2 = df[-5]
    except_sc = li[num:num+24*2] + li[num+24*2+2:num+24*2+2+(extended_round1+extended_round2)*2]
    except_sc = remove_pa(except_sc)
    score = [i for index,i in enumerate(except_sc) if index%2==1]

  except:
    num = 12
    round = int(li[0])+int(li[num-3])
    df =li[:num]
    map = df[4]
    result1 = df[0]; result2 = df[-3]
    extended_round1 = 0
    extended_round2 = 0
    map_time = df[5]
    first_half1 = df[2]; second_half1 = df[3]
    first_half2 = df[-5]; second_half2 = df[-4]
    score = [i for index,i in enumerate(li[num:num+round*2]) if index%2==1]



  if round <= 24:
    r = round*2+(24-round)
  else:
    r = round*2+2


  Con_sco = Conti_score(score,round)
  team1 = li[num+r+12:num+r+12+38*5]
  team2 = li[-38*5:]

  team1 = np.array(team1).reshape(5,38)
  team2 = np.array(team2).reshape(5,38)
  team_l = team1[0][1]
  team_r = team2[0][1]
  
  ov_1 = []
  ov_2 = []

  for i in range(5):
    player_l = team1[i][0]
    stat = team1[i][2:]
    stat0_l = [i for index,i in enumerate(stat) if index%3==0]
    stat1_l = [i for index,i in enumerate(stat) if index%3==1]
    stat2_l = [i for index,i in enumerate(stat) if index%3==2]
    stat1_l.insert(0,team_r);stat1_l.insert(0,team_l); stat1_l.insert(0,player_l)
    stat2_l.insert(0,team_r);stat2_l.insert(0,team_l); stat2_l.insert(0,player_l)
    stat1_l = stat1_l + [' ',map, map_time,first_half1,second_half1,Con_sco[0]]
    stat2_l = stat2_l + [' ',map, map_time,first_half1,second_half1,Con_sco[0]]
    ov_1 += [stat1_l]
    ov_2 += [stat2_l]

  for i in range(5):
    player_r = team2[i][0]
    stat = team2[i][2:]
    stat0_r = [i for index,i in enumerate(stat) if index%3==0]
    stat1_r = [i for index,i in enumerate(stat) if index%3==1]
    stat2_r = [i for index,i in enumerate(stat) if index%3==2]
    stat1_r.insert(0,team_l);stat1_r.insert(0,team_r); stat1_r.insert(0,player_r)
    stat2_r.insert(0,team_l);stat2_r.insert(0,team_r); stat2_r.insert(0,player_r)
    stat1_r = stat1_r + [' ',map, map_time,first_half2,second_half2,Con_sco[1]]
    stat2_r = stat2_r + [' ',map, map_time,first_half2,second_half2,Con_sco[1]]
    ov_1 += [stat1_r]
    ov_2 += [stat2_r]



  ov_column = ['Player','Team','VS_Team','R', 'ACS', 'K', 'D', 'A', 'K_D', 'KAST', 'ADR', 'HS%', 'FK', 'FD', 'FK_FD','TCT','Map','RunTime','First_half','Second_half','Conti_score']
  ov_1 = pd.DataFrame(ov_1, columns = ov_column)
  ov_2 = pd.DataFrame(ov_2, columns = ov_column)
  if TCT(ele) == 'CT':
    ov_1['TCT'] = ['CT','CT','CT','CT','CT','T','T','T','T','T']
    ov_2['TCT'] = ['T','T','T','T','T','CT','CT','CT','CT','CT']
  else:
    ov_2['TCT'] = ['CT','CT','CT','CT','CT','T','T','T','T','T']
    ov_1['TCT'] = ['T','T','T','T','T','CT','CT','CT','CT','CT']
  ov_1['Extended_round'] = extended_round1
  ov_2['Extended_round'] = extended_round2
  ov_1['Score'] = result1; ov_2['Score'] = result2
  if result1 > result2:
    ov_1['Winner'] = 1; ov_2['Winner'] = 0
  else:
    ov_1['Winner'] = 0; ov_2['Winner'] = 1
  overview_df = pd.concat([ov_1,ov_2])

  if len(li) != num+r+12+38*5+12+38*5:
    print('li Length Error!!!')

  return overview_df

Overview_DF = pd.DataFrame()

##### Match 들어가기 #####
pages = range(300,400)
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
        try:
          link = match[index_match].get_attribute("href")
        except:
          index_match +=1
          continue
        driver.execute_script('window.open("");')
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(link)
        #WebDriverWait(driver, 30).until(EC.presence_of_element_located(By.XPATH, '//*[@id="wrapper"]/div[3]/div[3]/div[1]/div[1]/div[1]/a/div/div[1]'))
        time.sleep(1)

        ##### Match 정보 #####
        Date = ''
        League = ''
        Stage = ''
        Patch = 0
        BO = ''
        try:
          match_data(3)
        except:
          index_match += 1
          continue

        for i in range(1,7):
          try:
            ele = driver.find_element(By.XPATH,f'//*[@id="wrapper"]/div[3]/div[3]/div[7]/div/div[3]/div[{i}]')
            print(i,'Complete')
            if ele.get_attribute('data-game-id') == 'all':
              print('all')
              continue
          except:
            print(i,'None')
            continue
          data_game_id = ele.get_attribute('data-game-id')
          print(data_game_id)

          text = ele.get_attribute('textContent')
          remove_set = {' '}
          text_list= list(text.split('\n'))
          li = [re.sub(('\\t|/|/s|PICK|AllAttackDefend'),'',i) for i in text_list]
          li = list(filter(None, li))
          li = [i for i in li if i not in remove_set]
          li = [re.sub(('\xa0'),'NaN',i) for i in li]

          if li == ['No data available for this match']:
            continue

          try:
            overview_df = overview(li,ele)
          except:
            continue

          overview_df['data_game_id'] = data_game_id
          Overview_DF = pd.concat([Overview_DF,overview_df],ignore_index=True)
          #print(overview_df)
        Overview_DF['Date'] = Date
        Overview_DF['League'] = League
        Overview_DF['Stage'] = Stage
        Overview_DF['Patch'] = Patch
        Overview_DF['BO'] = BO


        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(1)

        index_match += 1


Overview_DF.to_csv('C:/Users/WTA/crawler/Overview300-400.csv',index=False)
