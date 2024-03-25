#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import sys
import os
from os.path import join, abspath
#from openpyxl import load_workbook, Workbook
import shutil

import funcsYandexGis as yagis

import time
timer = time.time

from sqlalchemy import create_engine
import sqlite3

dict_service = {
    'яндекс':
    [
        'cheked_ya', 'ya_start', 'ya_time',
        'ya_total_cheked', 'ya_avg_time', 'ya_remain', 'ya_time_end'
    ],
    'гис':
    [
        'cheked_gis', 'gis_start', 'gis_time',
        'gis_total_cheked', 'gis_avg_time', 'gis_remain', 'gis_time_end'
    ]
}

#data_path = join('..', 'Data', 'ps1.xlsx')
#data_path = abspath(data_path)
#wbr = load_workbook(filename=data_path)
#ws = wbr['Тип']
#lst_type_ynd = [ws.cell(row=i, column=1).value
                #for i in range(2, ws.max_row + 1)
                #if ws.cell(row=i, column=1).value != None]
#lst_type_gis = [ws.cell(row=i, column=2).value
                #for i in range(2, ws.max_row + 1)
                #if ws.cell(row=i, column=2).value != None]


dict_type_ynd = {
    'КПК':
    [
        'Кредитный потребительский кооператив', 'Потребительская кооперация',
        'кредитный потребительский кооператив', 'потребительская кооперация'
    ],
    'СКПК':
    [
        'Сельскохозяйственный кредитный потребительский кооператив',
        'Кредитный потребительский кооператив',
        'Потребительская кооперация',
        'сельскохозяйственный кредитный потребительский кооператив',
        'потребительская кооперация'
    ]
}
dict_type_gis = {
    'КПК':
    [
        'Кредитные потребительские кооперативы',
        'Кредитный потребительский кооператив',
        'Группа кредитных потребительских кооперативов', 
        'Сельскохозяйственный потребительский перерабатывающе-сбытовой снабженческий кооператив',
        'Кредитный потребительский кооператив граждан'
    ],
    'СКПК':
    [
        'Сельскохозяйственные кредитные потребительские кооперативы',
        'Кредитные потребительские кооперативы',
        'Сельскохозяйственный кредитный потребительский кооператив',
        'Сельскохозяйственный потребительский перерабатывающий кооператив',
        'Кредитный потребительский кооператив'
    ]
}

data_path = join('..', 'Data', 'database.db')
engine = sqlite3.connect(data_path)
cur = engine.cursor()


def look_for(list_tmp):
    global start_list
    global n_adrs
    data_orgs, name_service = list_tmp
    list_service = dict_service[name_service]
    
    sql_exit_data = f'''
        INSERT INTO exit_data(
            counter,
            ogrn, 
            source, 
            name_in_source, 
            type_of_activity,
            site,
            name_gis) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
    
    
    # =============================================================================
    chrmdrvr_path = join('..', 'Data', 'chromedriver.exe')
    s = Service(chrmdrvr_path)
    options_chrome = webdriver.ChromeOptions()

    prefs = {
        "profile.managed_default_content_settings.images": 2,
        
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.plugins": 2,
        "profile.managed_default_content_settings.popups": 2,
        "profile.managed_default_content_settings.geolocation": 2,
        "profile.managed_default_content_settings.media_stream": 2,
        
        "profile.managed_default_content_settings.AnimatedImage": 2,
        "profile.managed_default_content_settings.Cookies": 2,
        "profile.managed_default_content_settings.Flash": 2,
        "profile.managed_default_content_settings.Silverlight": 2
    }
    
    options_chrome.add_experimental_option("prefs", prefs)

    if name_service == 'яндекс':
        options_chrome.add_argument('--headless')
    options_chrome.add_argument('--window-size=1000,900')
    options_chrome.add_argument('--start-maximized')
    options_chrome.add_argument('--disable-gpu')
    options_chrome.add_argument('--no-sandbox')
    options_chrome.add_argument('--disable-extensions')
    options_chrome.add_argument('disable-infobars') 
    
    global browser
    browser = webdriver.Chrome(service=s, options=options_chrome)

    start_0 = timer()
    data_orgs = data_orgs[start_list:]
    for org in data_orgs:
        n_adrs = str(org[0])
        lst_type_ynd = dict_type_ynd[org[4]]
        lst_type_gis = dict_type_gis[org[4]]
        start_1 = timer()
        print(f'\n\n{org}')
        rslts = []
        if name_service == 'яндекс':
            rslts = yagis.check_ya(org, browser, rslts, lst_type_ynd)
        if name_service == 'гис':
            rslts = yagis.check_gis(org, browser, rslts, lst_type_gis)
        
        start_2 = timer()
        for rslt in rslts:
            rslt = list(org)[:2] + rslt[:]
            cur.execute(sql_exit_data, rslt)
            engine.commit()
            
        #hms = time.strftime('%H:%M:%S', time.gmtime(start_1 + 3 * 3600))
        date_hms = time.ctime(start_1)
        sql_query = f'''
            UPDATE enter_data
            SET {list_service[0]}="+",
                {list_service[1]}="{date_hms}",
                {list_service[2]}={round(timer() - start_1, 2)},
                time_write={round(timer() - start_2, 2)}
            WHERE counter={n_adrs}
            '''
        cur.execute(sql_query)
        engine.commit()

        start_list += 1

    engine.close()
    browser.quit()


def startLookFor(list_tmp):
    global start_list
    global n_adrs
    _, name_service = list_tmp
    list_service = dict_service[name_service]
    start_list = 0
    counterAttempts = 1
    while True:
        try:
            look_for(list_tmp)
            break
        except:
            try:
                browser.quit()
            except:
                pass
            if counterAttempts == 3:
                start_list += 1
                counterAttempts = 1
                sql_query = f'''
                    UPDATE enter_data
                    SET {list_service[0]}="-"
                    WHERE counter={n_adrs}
                    '''
                cur.execute(sql_query)
                engine.commit()                
            else:
                counterAttempts += 1


def startLookFor_2(list_tmp):
    global start_list
    start_list = 0
    look_for(list_tmp)
    

def get_set_SQL(name_service, num_query, start_0=0, empty_rows=0, numProccess=0):
    list_service = dict_service[name_service]
    if num_query == 1:  # учесть, что начала поиска в сервисе должно быть больше начала общего поиска
        sql_query = f'''
            SELECT COUNT(ogrn) AS empty_rows
            FROM enter_data
            WHERE {list_service[0]} IS NULL OR {list_service[0]}=""
            '''
        return cur.execute(sql_query).fetchall()
    if num_query == 2:
        sql_query = f'''
            SELECT (SUM({list_service[2]}) / COUNT({list_service[2]})) AS avg_time, 
                   COUNT({list_service[2]}) AS count_checked
            FROM enter_data
            WHERE {list_service[0]}="+"
            '''
        avg_time, count_checked = cur.execute(sql_query).fetchall()[0]
        if avg_time:
            end_sec = start_0 + avg_time * empty_rows / numProccess
            end_dt = time.ctime(end_sec)
            sql_query = f'''
                UPDATE calc
                SET {list_service[3]}="{count_checked}",
                    {list_service[4]}="{round(avg_time,1)}",
                    {list_service[5]}="{empty_rows}",
                    {list_service[6]}="{end_dt}"
                '''
            cur.execute(sql_query)
            engine.commit()

timeout_calc = 30
copy_path = join('..', 'Data', 'copy_')
copy_path = abspath(copy_path)
def seeTimeEnd(start_0, numProccessForYa, numProccessForGis):
    i_repeat = 0
    while True:
        time.sleep(timeout_calc)
        ya_empty_rows = get_set_SQL('яндекс', 1)[0][0]
        gis_empty_rows = get_set_SQL('гис', 1)[0][0]
        # if (ya_empty_rows or gis_empty_rows) and i_repeat != 60/timeout_calc * 5:
        if ya_empty_rows or gis_empty_rows:
            get_set_SQL('яндекс', 2, start_0, ya_empty_rows, numProccessForYa)
            get_set_SQL('гис', 2, start_0, gis_empty_rows, numProccessForGis)
        else:
            break
        if i_repeat * timeout_calc % 3600 == 0:
            hms = time.strftime('%H_%M_%S', time.gmtime(timer()))
            shutil.copyfile(data_path, copy_path + hms + '.db')
        i_repeat += 1