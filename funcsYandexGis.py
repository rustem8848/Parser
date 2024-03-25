#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time
from datetime import datetime
import urllib.request
import ssl


timeout = 7
list_sub = ['республика', 'край', 'область',
    'автономный округ', 'автономная область',
    'респ', 'обл',
    'район', 'россия']
def cut(adrs):
    lst_adrs = adrs.split(',')
    if lst_adrs[0].strip().isdigit():
        lst_adrs.pop(0)
    lst_adrs_new = []
    if len(lst_adrs) > 1:
        for l in lst_adrs:
            if not [x for x in list_sub if x.lower() in l.lower()]:
                lst_adrs_new.append(l)
    else:
        lst_adrs_new = lst_adrs
    return ','.join(lst_adrs_new)


'''
------------------------------
# Яндекс
------------------------------
'''
def check_ya(org, browser, rslts, lst_type_ynd):
    browser.get('https://yandex.ru/maps/')

    # поиск по адресу
    str_adrs = cut(org[3])

    WebDriverWait(browser, poll_frequency=0.2, timeout=timeout). \
        until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input.input__control')
            ))

    browser.find_element(
        By.CSS_SELECTOR, 'input.input__control'
    ).send_keys(str_adrs)

    browser.find_element(
        By.CSS_SELECTOR,
        'button.button._view_search._size_medium'
    ).click()
    
    try:
        WebDriverWait(browser, poll_frequency=0.2, timeout=timeout). \
            until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'div.tabs-select-view__title._name_inside')
                ))
    except:
        try:
            browser.find_element(
                By.XPATH,
                '//*[text()="Результаты могут быть неточными"]') 
        except:
            pass
        else:
            browser.find_element(
                By.CSS_SELECTOR,
                'div.search-snippet-view__title'
            ).click()
            
    try:
        browser.find_element(
            By.CSS_SELECTOR,
            'div.tabs-select-view__title._name_inside'
        ).click()
    except:
        rslts.append(
            ['Яндекс',
             'по данному адресу организации не зарегистрированы',
             '-', '-', '-'])
    else:
        # раскрываем весь перечень организаций
        WebDriverWait(browser, poll_frequency=0.2, timeout=timeout). \
            until(
                EC.visibility_of_element_located(
                    (By.XPATH,
                     '//span[@class="button__text" and text()="Все категории"]')
                ))
        elements_ = browser.find_elements(
            By.XPATH,
            '//a[@class="search-snippet-view__link-overlay _focusable"]')
        cnt_org_1 = len(elements_)
        cnt_org_2 = 0
        while cnt_org_1 != cnt_org_2:
            cnt_org_1 = len(elements_)
            browser.execute_script(
                'return arguments[0].scrollIntoView(true);', elements_[-1])
            time.sleep(1)
            elements_ = browser.find_elements(
                By.XPATH,
                '//a[@class="search-snippet-view__link-overlay _focusable"]')
            cnt_org_2 = len(elements_)

        # сохраняем организации с соответствующей деятельностью
        lst_cmp = []
        for type_org in lst_type_ynd:
            elms = browser.find_elements(By.XPATH,
                        '//a[@class="search-business-snippet-view__category" and ' +
                            'text()="' + type_org + '"]//ancestor::' +
                        'div[@class="search-snippet-view__body _type_business"]' +
                        '//div//a[@class="search-snippet-view__link-overlay _focusable"]')
            for elm in elms:
                lst_cmp.append(
                    (elm.text or elm.get_attribute('text'),
                     elm.get_attribute('href'), type_org)
                )

        lst_cmp = set(lst_cmp)
        print(lst_cmp)
        
        
        # проверяем перечень организаций
        for cmp in lst_cmp:
            browser.get(cmp[1])

            # поиск сайта
            site_work = '-'
            try:
                site_org = browser.find_element(
                    By.CSS_SELECTOR,
                    'a.business-urls-view__link').get_attribute('href')
            except:
                site_org = '-'
            else:
                pass
            rslts.append(
                ['Яндекс', cmp[0], cmp[2], site_org, '-'])
        if not lst_cmp:
            rslts.append(
                ['Яндекс',
                 'по данному адресу отсутствуют организации с соответствующей деятельностью',
                 '-', '-', '-'])

    return rslts


'''
------------------------------
# 2ГИС
------------------------------
'''
def check_gis(org, browser, rslts, lst_type_gis):
    str_adrs = cut(org[3])
    browser.get('https://2gis.ru/')
    # time.sleep(0.5)
    WebDriverWait(browser, poll_frequency=0.2, timeout=timeout). \
        until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input._1gvu1zk')
            ))

    # поиск по адресу
    browser.find_element(
        By.CSS_SELECTOR,
        'input._1gvu1zk').send_keys(str_adrs)
    browser.find_element(
        By.CSS_SELECTOR,
        'input._1gvu1zk').send_keys(Keys.ENTER)
    # time.sleep(2)
    WebDriverWait(browser, poll_frequency=0.2, timeout=timeout). \
        until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[text()="Места"]')
            ))

    # выявлено точное совпадение?
    try:
        href_org = browser.find_element(
            By.XPATH, '//a[text()="Инфо"]')
    except:
        # если нет, переходим по первой ссылке
        href_org = WebDriverWait(
            browser, poll_frequency=0.2, timeout=timeout). \
            until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     '//div[@class="_1kf6gff"]/div/a[@class="_1rehek"]')
                ))

        browser.get(href_org.get_attribute('href'))

        WebDriverWait(browser, poll_frequency=0.2, timeout=timeout). \
            until(
                EC.presence_of_element_located(
                    (By.XPATH, '//a[text()="Инфо"]')
                ))
    
    try:
        href_org = browser.find_element(By.XPATH, '//a[text()="В здании"]')
    except:
        rslts.append(
            ['2ГИС',
             'по данному адресу организации не зарегистрированы',
             '-', '-', '-'])
    else:
        browser.get(href_org.get_attribute('href'))
        # раскрываем весь перечень организаций
        f1 = 0
        f_count = 0
        while f1 == 0 and f_count < 100:
            try:
                browser.find_element(
                    By.XPATH, '//button[text()="Добавить организацию"]')
            except:
                elements_ = browser.find_elements(
                    By.XPATH,
                    '//div[@class="_1kf6gff"]/div/a[@class="_1rehek"]')                
                #elements_ = browser.find_elements(
                #    By.XPATH,
                #    '//div[@class="_1hf7139"]/div/a[@class="_1rehek"]')
                browser.execute_script(
                    'return arguments[0].scrollIntoView(true);', elements_[-1])
                time.sleep(0.5)
                f_count += 1
            else:
                f1 = 1
       
        # ...
        # save organizations with neccessary activity
        # сохраняем организации с соответствующей деятельностью
        # ...
        lst_cmp = []
        # поиск блок с информацией про организации
        elements = browser.find_elements(
            By.XPATH,
            '//div[@class="_1kf6gff"]')         
        for elm in elements:
            # поиск организации
            elm_org = elm.find_element(
                By.XPATH, './/div/a[@class="_1rehek"]'
            )
            name_org = elm_org.get_attribute('textContent')
            link_org = elm_org.get_attribute('href')
            try:
                # поиск типа деятельностью
                type_org = elm.find_element(
                    By.XPATH,
                    './/div[@class="_1idnaau"]/span[@class="_oqoid"]'
                ).get_attribute('textContent')
            except:
                type_org = 'EMPTY'
            if type_org in lst_type_gis:
                lst_cmp.append([name_org, link_org, type_org])
        '''
        lst_cmp = []
        elms_name = browser.find_elements(By.XPATH,
                        '//div[@class="_1p8iqzw"]/span[@class="_oqoid"]//ancestor::' +
                        'div[@class="_1hf7139"]/div[@class="_1h3cgic"]/a')
        elms_type = browser.find_elements(By.XPATH,
                        '//div[@class="_1p8iqzw"]/span[@class="_oqoid"]')
        nms = [e.get_attribute('textContent') for e in elms_name]
        tps = [e.get_attribute('textContent') for e in elms_type]
        lns = [e.get_attribute('href') for e in elms_name]
        for elm_n, elm_t, elm_l in zip(nms, tps, lns):
            for type_org in lst_type_gis:
                if type_org in elm_n or type_org in elm_t:
                    lst_cmp.append([elm_n, elm_l, type_org])
                    break
        '''
        # проверяем перечень организаций
        for cmp in lst_cmp:
            browser.get(cmp[1])
            # time.sleep(1.5)
            WebDriverWait(browser, poll_frequency=0.2, timeout=timeout). \
                until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//span[@class="_er2xx9"]/a[@class="_2lcm958"]')
                    ))

            # поиск названия организации, опубликовавшего контакты
            name_2gis = '-'
            try:
                elm = browser.find_element(
                    By.XPATH, '//div[@class="_1q1z1sxo"]/span[@class="_14quei"]/'
                    + 'span[@class="_1w9o2igt"]/span/span[@class="_1x3o8eh"]')
            except:
                pass
            else:
                name_2gis = elm.text or elm.get_attribute('text')

            # поиск сайта
            site_work = '-'
            try:
                elm = browser.find_element(By.XPATH,
                                           '//div[@class="_49kxlr"]/span/div/a')
            except:
                site_org = '-'
            else:
                site_org = elm.text or elm.get_attribute('text')
            rslts.append(
                ['2ГИС', cmp[0], cmp[2], site_org, name_2gis])
        if not lst_cmp:
            rslts.append(
                ['2ГИС',
                 'по данному адресу отсутствуют организации с соответствующей деятельностью',
                 '-', '-', '-'])
    return rslts

