#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from multiprocessing import Pool
from functools import partial
import math
import mainLookFor as mainFile

from os.path import join, abspath
from sqlalchemy import create_engine
import sqlite3

import time
timer = time.time

def setBorder(proc_num, total_num, upper):
     a = step * proc_num
     b = a + step
     return a, b

def startFunc(func):
     return func()


dict_service = {'яндекс': 'cheked_ya',
                'гис': 'cheked_gis'}
data_path = join('..', 'Data', 'database.db')
engine = sqlite3.connect(data_path)
cur = engine.cursor()
def identifyList(name_service):
     check_column = dict_service[name_service]
     
     sql_query = f'''
         SELECT counter,ogrn,name,address,type
         FROM enter_data
         WHERE {check_column} IS NULL OR 
               {check_column}="" OR 
               {check_column}="-"
         '''
     '''
     sql_query = f''
         SELECT counter,ogrn,name,address,type
         FROM enter_data
         WHERE {check_column} IS NULL OR 
               {check_column}=""
         ''
     '''
     return cur.execute(sql_query).fetchall()


dataOrgsYa = identifyList('яндекс')
dataOrgsGis = identifyList('гис')

start_0 = timer()
numProccess = 3
numProccessForYa = 1
numProccessForGis = 1

# the following 3 lines for testing
# countForTesting = 5
# dataOrgsGis = dataOrgsGis[:countForTesting]
# dataOrgsYa = dataOrgsYa[:countForTesting]


listFunc = []
for i in range(0, numProccessForYa):
     step = math.ceil(len(dataOrgsYa) / numProccessForYa)
     minBorder, maxBorder = setBorder(i, numProccessForYa, len(dataOrgsYa))
     f = partial(
         mainFile.startLookFor,
         [dataOrgsYa[minBorder:maxBorder], 'яндекс']
     )
     listFunc.append(f)


for i in range(0, numProccessForGis):
     step = math.ceil(len(dataOrgsGis) / numProccessForGis)
     minBorder, maxBorder = setBorder(i, numProccessForGis, len(dataOrgsGis))
     f = partial(
         mainFile.startLookFor,
         [dataOrgsGis[minBorder:maxBorder], 'гис']
     )
     listFunc.append(f)
    

#f = partial(
    #mainFile.startLookFor,
    #[dataOrgsGis, 'гис']
#)
#listFunc.append(f)


f = partial(
    mainFile.seeTimeEnd,
    start_0, numProccessForYa, numProccessForGis
)
listFunc.append(f)

engine.close()

# comment the folowing three lines for testing
'''
if __name__ == '__main__':
     p = Pool(processes=numProccess)
     p.map(startFunc, listFunc)
'''

# the following five lines for testing
# dataOrgsGis = dataOrgsGis[:1]
# dataOrgsYa = dataOrgsYa[:1]
# print(dataOrgsGis)
mainFile.startLookFor_2([dataOrgsGis, 'гис'])
# mainFile.startLookFor_2([dataOrgsYa, 'яндекс'])

# ttl_sec = timer() - start_0
# ttl_tm = time.gmtime(ttl_sec)
# hms = time.strftime('%H:%M:%S', ttl_tm)
# print(f'\n\n\nВремя анализа {hms}')


print('END')
