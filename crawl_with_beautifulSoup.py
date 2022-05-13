import multiprocessing
import random
import sqlite3
import time
from selenium.webdriver.common.by import By
from selenium import webdriver as selenium_webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

HOW_MANY_THREAD_DO_YOU_NEED = 3

LINK_CHROMEDRIVER = r"chromedriver.exe"

def initDriver(IS_HEADLESS = False):
    options = selenium_webdriver.ChromeOptions()
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.headless = IS_HEADLESS
    prefs = {
        "profile.managed_default_content_settings.images": 2
    }
    options.add_experimental_option("prefs", prefs)
    return selenium_webdriver.Chrome(service=Service(
        LINK_CHROMEDRIVER), options=options)

def crawl(driver, second_link):
    try:
        link = second_link[random.randint(0, len(second_link))]
        crawl_data_with_soup(driver, link[0], link[1], link[2])
        this_link_is_used(link[0])
        second_link.remove(link)
    except:
        pass

def push_to_database(listing_type, name, location, industry, asking_price, revenue, cash_flow, ebitda, established):
    try:
        cmd = '''insert into results  ([Listing type] ,
                Name,
                Location,
                Industry,
                [Asking Price],
                Revenue,
                [Cash flow],
                EBITDA,
                [Established date]) values  (\'''' + str(listing_type) +"\', \'"+str(name)+"\', \'"+str(location)+"\', \'"+str(industry)+"\', \'"+str(asking_price)+"\', \'"+str(revenue)+"\', \'"+str(cash_flow)+"\', \'"+str(ebitda)+"\', \'"+str(established)+"\')"
        with sqlite3.connect("database.db") as conn:
            conn.execute(cmd)
            conn.commit()
    except:pass

def get_values(soup, title):
    title_tags = soup.select('span.title')
    for i in range(len(title_tags)):
        text = title_tags[i].text.lower()
        if(text.find(title.lower()) != -1):
            return title_tags[i].parent.find('b').text.replace("\n", "").replace("  ", "")
    return 'NULL'

def crawl_data_with_soup(driver, url, listing_type, industry):
    try:
        driver.get("view-source:"+url)
        soup = BeautifulSoup(driver.find_element(By.TAG_NAME, "html").text, 'html.parser')
    except:return

    try:
        name = soup.find("h1").text.replace("\n", "").replace("  ", "")
        location = soup.select_one('h2.gray').text.replace("\n", "").replace("  ", "")
        asking_price = get_values(soup, 'Asking Price:')
        revenue = get_values(soup, 'Revenue')
        cash_flow = get_values(soup, 'Cash flow')
        ebitda = get_values(soup, 'EBITDA')
        established  = get_values(soup, 'Established')
    except:return
    conti = 1
    while(conti):
        try:
            push_to_database(listing_type, name, location, industry, asking_price, revenue, cash_flow, ebitda, established)
            conti = 0
        except Exception as e:
            print(str(e))
            if(str(e).find("database is locked") == -1):return
            print("Disconnected with database!")
            time.sleep(2)

def this_link_is_used(l):
    cmd = "update data set status = 1 where link = '"+str(l)+"'"
    conti = 1
    while(conti):
        try:
            with sqlite3.connect("database.db") as conn:
                conn.execute(cmd)
            conti = 0
        except Exception as e:
            print(str(e))
            if(str(e).find("database is locked") == -1):return
            print("Disconnected with database!")
            time.sleep(2)
    conn.commit()

def get_records_left_in_database():
    cmd = "SELECT count(*) FROM data where status = 0;"
    with sqlite3.connect("database.db") as conn:
        cursor = conn.execute(cmd)
        conn.commit()
    for i in cursor:
        result = i[0]
        break
    print(result, " records left.")
    if(result == 0):
        return False
    return True

def process():
    cmd = "SELECT link, [Listing type], industry FROM data where status = 0;"
    with sqlite3.connect("database.db") as conn:
        cursor = conn.execute(cmd)
        conn.commit()
    second_link = []
    for i in cursor:
        second_link.append(i)
    
    driver = initDriver()
    # range(HOW_MANY_THREAD_DO_YOU_NEED)

    while(get_records_left_in_database()):
        crawl(driver, second_link)
    input("Successful!")

def crawl_with_beautifulSoup():
    myDictionary = {}
    for i in range(HOW_MANY_THREAD_DO_YOU_NEED):
        myDictionary[i] = multiprocessing.Process(target=process, args=())

    for i in range(HOW_MANY_THREAD_DO_YOU_NEED):
        # starting process
        myDictionary[i].start()

    for i in range(HOW_MANY_THREAD_DO_YOU_NEED):
        # wait until process is finished
        myDictionary[i].join()

if __name__ == '__main__':
    crawl_with_beautifulSoup()
