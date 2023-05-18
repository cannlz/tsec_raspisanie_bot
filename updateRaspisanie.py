import requests
from bs4 import BeautifulSoup
import re
import os, glob
import time
from selenium import webdriver
import sqlite3 as sq
from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from testExelRead import *



my_secret = os.environ['my_secret']
bot = Bot(my_secret)
dp = Dispatcher(bot, storage=MemoryStorage())

baseMain = sq.connect('tsec_base.db')
cur = baseMain.cursor()

async def checkDriver(typeupdate):

    listOtdeleniya = ["rasp_ites", "rasp_tc", "rasp_spsipb", "rasp_rpco", "rasp_ppkrc"]
    countSoup = [0, 1, 3, 4, 5]
    listheigtOrig = [1300, 1300, 1300, 1100, 1300]
    listwheightOrig = [2500, 1800, 2400, 1300, 2100]
    for countStart in countSoup:
        
        if countStart == 3 or countStart == 5:
            countVerify = countStart - 1
            foldername = listOtdeleniya[countVerify]
            listheigt = listheigtOrig[countVerify]
            listwheight = listwheightOrig[countVerify]
        elif countStart == 4:
            countVerify = countStart - 1
            foldername = listOtdeleniya[countVerify]
            listheigt = listheigtOrig[countVerify]
            listwheight = listwheightOrig[countVerify]
        else:
            foldername = listOtdeleniya[countStart]
            listheigt = listheigtOrig[countStart]
            listwheight = listwheightOrig[countStart]
        print(f"{foldername}\n{countStart}")
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        r = requests.get(url=url)
        soup = BeautifulSoup(r.text, "lxml")

        articles_cards = soup.find_all('div', class_='acc')[countStart].find_all('div', class_='acc_body')
        linkcheck = soup.find_all('div', class_='acc_body')[countStart].find("table").find("tbody").find_all("a", href=True)
        check = 0

        for article in articles_cards:
            antifloodpopup = 0
            for i in linkcheck:
                try:                        
                    article_name = article.find("table").find("tbody").find_all("a")[check].text.strip()
                    s = article_name.split('(')[0]
                    dateRasp = re.sub('РАСПИСАНИЕ УЧЕБНЫХ ЗАНЯТИЙ НА ', '', s) # Выводим дату
                    if "РАСПИСАНИЕ УЧЕБНЫХ ЗАНЯТИЙ НА " in article_name:
                        fullTextlink = i.text # Получаем полноценный текст ссылки
                        try:
                            article_url = i.get('href') # Получаем сслыку
                            #print(article_url)
                            if baseMain.execute(f'SELECT * FROM {foldername} WHERE link = "{article_url}"').fetchone() == None:
                                output_path = await downloadExel(article_url, fullTextlink, foldername) # загружаем exel таблицу для текстового варианта
                                chrome_options = Options()

                                chrome_options.add_argument('--no-sandbox')
                                chrome_options.add_argument("--disable-gpu")
                                chrome_options.add_argument("--headless")
                                chrome_options.add_argument('--disable-dev-shm-usage')
                                chrome_options.add_argument('--disable-crash-reporter')

                                chrome_options.add_argument("--disable-dev-shm-usage")
                                chrome_options.add_argument("--disable-renderer-backgrounding")
                                chrome_options.add_argument("--disable-background-timer-throttling")
                                chrome_options.add_argument("--disable-backgrounding-occluded-windows")
                                chrome_options.add_argument("--disable-client-side-phishing-detection")
                                chrome_options.add_argument("--disable-oopr-debug-crash-dump")
                                chrome_options.add_argument("--no-crash-upload")
                                chrome_options.add_argument("--disable-extensions")
                                chrome_options.add_argument("--disable-low-res-tiling")
                                chrome_options.add_argument("--log-level=3")
                                chrome_options.add_argument("--silent")
                                driver = webdriver.Chrome(options=chrome_options)
                                driver.get(article_url)

                                S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+ X)
                                driver.set_window_size(listheigt, listwheight)  # May need manual adjustment
                                tables = [":10", ":1g", ":1w"]
                                for i in tables:
                                    try:
                                        driver.find_element(By.XPATH, '//*[@id="' + i + '"]').click()
                                        photo = (f"{foldername}/{fullTextlink}.png")
                                        driver.save_screenshot(photo)
                                        try:
                                            if i != ":10":
                                                datefromList = driver.find_element(By.CLASS_NAME, "docs-sheet-tab-name").text
                                                driver.quit()
                                                baseMain.execute(f"INSERT INTO {foldername}(date, preview_text, link, image, exelpath) VALUES(?,?,?,?,?)",(datefromList, fullTextlink, article_url, photo, output_path))
                                                baseMain.commit()
                                            else:
                                                driver.quit()
                                                baseMain.execute(f"INSERT INTO {foldername}(date, preview_text, link, image, exelpath) VALUES(?,?,?,?,?)",(dateRasp, fullTextlink, article_url, photo, output_path))
                                                baseMain.commit()
                                        except:
                                            driver.quit()
                                            baseMain.execute(f"INSERT INTO {foldername}(date, preview_text, link, image, exelpath) VALUES(?,?,?,?,?)",(dateRasp, fullTextlink, article_url, photo, output_path))
                                            baseMain.commit()
                                        try:
                                            if typeupdate == 'update' and antifloodpopup == 0:
                                                antifloodpopup = 1
                                                foldersGroups = {
                                                'rasp_ites': 'ИТЭС',
                                                'rasp_tc': 'ТС',
                                                'rasp_spsipb': 'СПСиПБ',
                                                'rasp_rpco': 'РЦПО',
                                                'rasp_ppkrc': 'ППКРС'
                                                }
                                                if foldername in foldersGroups:
                                                    namegroup = foldersGroups[foldername]
                                                    dataUser = baseMain.execute(f'SELECT user_id FROM users WHERE selected_group = "{namegroup}"').fetchall()
                                                    for i in dataUser:
                                                        await bot.send_message(i[0],f'🟢Новое Расписания занятий отделения {namegroup}', disable_notification=True)
                                        except Exception as e:
                                            print(e)
                                            pass
                                    except Exception as e:
                                        print("Второго листа не найдено")
                                        driver.quit()
                                        break           
                        except Exception as e: # В случае ошибки очищаем всё 
                            article_url = ''
                            article_name = ''
                            print("Ошибка uri", e)
                except: 
                    article_name = ''
                    article_url = ''
                    print("Ошибка name")
                check += 1           

async def deleteAll(): #Тут async

    baseMain.execute(f'UPDATE users SET checkpopup = 0 ')
    baseMain.commit()
    time.sleep(2)
    baseMain.execute("DELETE FROM rasp_ites")
    baseMain.commit()
    for file in glob.glob("rasp_ites/*"):
        os.remove(file)
    time.sleep(2)
    baseMain.execute("DELETE FROM rasp_ppkrc")
    baseMain.commit()
    for file in glob.glob("rasp_ppkrc/*"):
        os.remove(file)
    time.sleep(2)
    baseMain.execute("DELETE FROM rasp_rpco")
    baseMain.commit()
    for file in glob.glob("rasp_rpco/*"):
        os.remove(file)
    time.sleep(2)
    baseMain.execute("DELETE FROM rasp_spsipb")
    baseMain.commit()
    for file in glob.glob("rasp_spsipb/*"):
        os.remove(file)
    time.sleep(2)
    baseMain.execute("DELETE FROM rasp_tc")
    baseMain.commit()
    for file in glob.glob("rasp_tc/*"):
        os.remove(file)
    print("deleted")
    await checkDriver("delete") #Тут await