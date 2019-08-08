# -*- coding: utf-8 -*-  

from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
import requests
import MySQLdb
import time
import random
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

db = MySQLdb.connect("localhost", "root", "Lt870702@", "anjuke", charset='utf8' )

def histGraph():
    cursor = db.cursor()
    sql = "SELECT price_area from sec_hand_new"
    cursor.execute(sql)
    arr = np.array(cursor.fetchall())

    fig, ax = plt.subplots()
    n, bins, patches = ax.hist(arr[:, 0], bins=20, normed=0, facecolor='red', alpha=0.75)
    ax.set_xticks(bins)
    plt.xlabel("单价/元")
    plt.ylabel("套数/套")
    plt.title("西安市二手房房价分布")

    mean = np.mean(arr)
    std = np.std(arr)
    plt.axvline(mean)
    plt.axvline(mean-std)
    plt.axvline(mean+std)

    plt.show()



def praseHouseInfo(link):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    r=requests.get(link, headers=headers)
    soup=BeautifulSoup(r.text, 'lxml')
    house_list=soup.find_all('li', class_='list-item')

    cursor = db.cursor()
    for house in house_list:
        name = house.find('div', class_='house-title').a.text.strip()
        price = house.find('span', class_='price-det').text.strip()
        price_area = house.find('span', class_='unit-price').text.strip()#单位面积
        no_room = house.find('div', class_='details-item').span.text#几室几厅
        area = house.find('div', class_='details-item').contents[3].text
        floor = house.find('div', class_='details-item').contents[5].text
        year = house.find('div', class_='details-item').contents[7].text
        #broker=house.find('span',class_='brokername').text
        #broker=broker[1:]
        address = house.find('span', class_='comm-address').text.strip()
        tag_list = house.find_all('span', class_='item-tags')
        tags = [i.text for i in tag_list]
        tags = ','.join(tags)

        print(name)
        price = float(price[:-1:])
        price_area = float(price_area[:-4:])
        area = float(area[:-2:])
        year = int(year[:4:])

        sql = "SELECT count(1) from sec_hand_new WHERE name='%s' and price='%s'" % (name, price)
        cursor.execute(sql)
        cnt = cursor.fetchone()[0]
        if cnt >= 1:
            print "--repeat:", name, ":", cnt
            continue

        sql = "INSERT INTO sec_hand_new(name,price,price_area,\
                  no_room,area,floor,year,address,tags)\
                 VALUES ('%s', %f, %f, '%s', '%s', '%s', '%s', '%s', '%s')" \
                % (name, price, price_area, no_room, area, floor, year, address, tags)

        cursor.execute(sql)
        db.commit()


def getAllHouses():
    link = 'https://beijing.anjuke.com/sale/p'
    for i in range(1, 200):
        tlink = link + str(i) + "/#filtersort"
        print(tlink)
        praseHouseInfo(tlink)
        time.sleep(random.random() + 0.2)

if __name__ == '__main__':
    #getAllHouses()
    histGraph()