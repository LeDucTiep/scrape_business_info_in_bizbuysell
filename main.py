import multiprocessing
import random
import sqlite3
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

DATABASE_PATH = "database.db"

# it will open 4 browsers for scraping data in the second page
HOW_MANY_THREAD_DO_YOU_NEED = 4

# LINK_CHROMEDRIVER = "/media/tiepl/New Volume/crawl_freelancer/chromedriver"
# LINK_CHROMEDRIVER = r"chromedriver.exe"

Listing_type = ''


def initDriver(IS_HEADLESS=False) -> webdriver:
    options = Options()
    options.add_argument("--disable-blink-features")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.headless = IS_HEADLESS
    # set to 2: disable loading image
    # set to 1: enable ...
    options.set_preference(
        "permissions.default.image", 2)
    return webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)


def crawl_link(driver, industry):
    global Listing_type
    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "h3.title.ng-star-inserted")))
    except:
        pass

    try:
        temp = driver.execute_script(
            "return document.getElementsByClassName('listing-container')[0].children")
    except:
        return

    for i in temp:
        try:
            cmd = "insert into data(link, [Listing type], industry) values ('"+i.find_element(
                By.TAG_NAME, "a").get_attribute('href')+"', '"+Listing_type+"', '"+industry+"')"
            with sqlite3.connect(DATABASE_PATH) as conn:
                conn.execute(cmd)
                conn.commit()
        except:
            pass


def close_dialog():
    click_no_thank(driver)
    click_close_menu(driver)


def wait_until_Listing_type_displayed(driver):
    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.franchise-op")))
    except:
        pass

def click_listing_type_button(driver):
    try:
        driver.execute_script(
        "document.getElementsByClassName('btn filter-bar listing-types-button listing-type')[0].click()")
    except:pass

def click_industries_button(driver):
    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "hlSelectCategories"))).click()
    except:
        pass


def click_for_more_industries(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.all-industries-option.ng-tns-c6-3.ng-star-inserted"))).click()
    except:
        click_industries_button(driver)
        click_for_more_industries(driver)


def get_all_link(driver, Established_business, Startups, Asset_sales):
    global Listing_type
    driver.get(r'https://www.bizbuysell.com/businesses-for-sale/')

    # click listing-types-button
    click_listing_type_button(driver)
    wait_until_Listing_type_displayed(driver)

    # click "Established business,..." box
    if(Established_business):
        Listing_type += "Established business, "
        driver.execute_script(
            'document.getElementsByTagName("input")[0].click()')
    if(Asset_sales):
        Listing_type += "Asset sales, "
        driver.execute_script(
            'document.getElementsByTagName("input")[1].click()')
    if(Startups):
        Listing_type += "Startups, "
        driver.execute_script(
            'document.getElementsByTagName("input")[3].click()')
    
    # "Established business, Startups" = "Established business, Startups, " (https://www.w3schools.com/python/python_strings_slicing.asp)
    Listing_type = Listing_type[:-2]

    click_listing_type_button(driver)

    industries_length = 19
    for index_of_industries in range(industries_length):
        close_dialog()
        # try:
        driver.execute_script(
            "window.scrollTo(0, 0);")
        close_dialog()
        click_industries_button(driver)
        # except:
        #     close_dialog()

        # try:
        close_dialog()
        click_for_more_industries(driver)
        time.sleep(1)
        close_dialog()

        # clear all button clicked
        driver.execute_script(
            "document.getElementsByClassName('btn filter cta inverse cancel')[0].click()")
        time.sleep(1)
        # get data from elements
        industries_tag = driver.find_elements(By.TAG_NAME, "td")
        industries_length = len(industries_tag)
        industries_tag[index_of_industries].click()
        industry = industries_tag[index_of_industries].text
        time.sleep(1)
        close_dialog()
        # Click "apply"
        driver.execute_script(
            "document.getElementsByClassName('btn filter cta')[0].click()")
        close_dialog()

        click_industries_button(driver)
        time.sleep(5)
        page = 1
        while(page < 201):
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            close_dialog()
            crawl_link(driver, industry)
            page += 1
            try:
                close_dialog()

                # next page by click the "next" button
                WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.bbsPager_next.ng-star-inserted"))).click()
                # driver.execute_script("document.getElementsByClassName('bbsPager_next ng-star-inserted')[0].click()")
            except Exception as e:
                if(str(e).find("properties of undefined")):
                    page = 999


def click_no_thank(driver):
    try:
        driver.find_element(By.CSS_SELECTOR, "button.btn.nt").click()
    except:
        pass


def click_close_menu(driver):
    try:
        driver.execute_script(
            "document.getElementsByClassName('close-menu close-chip')[0].click()")
    except:
        pass


def get_values(driver, title):
    for i in range(len(driver.find_elements(By.CLASS_NAME, "title"))):
        text = driver.find_elements(By.CLASS_NAME, "title")[i].text.lower()
        if(text.find(title.lower()) != -1):
            return driver.find_elements(By.CLASS_NAME, "title")[i].find_element(By.XPATH, "..").find_element(By.TAG_NAME, "b").text
    return 'NULL'


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
                [Established date]) values  (\'''' + str(listing_type) + "\', \'"+str(name)+"\', \'"+str(location)+"\', \'"+str(industry)+"\', \'"+str(asking_price)+"\', \'"+str(revenue)+"\', \'"+str(cash_flow)+"\', \'"+str(ebitda)+"\', \'"+str(established)+"\')"
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute(cmd)
            conn.commit()
    except:
        pass


def crawl_data(driver, url, listing_type, industry):
    try:
        driver.get(url)
    except:
        return
    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "hlWatchListing")))
    except:
        pass

    try:
        name = driver.find_element(By.TAG_NAME, 'h1').text
        location = driver.find_element(By.CSS_SELECTOR, 'h2.gray').text
        asking_price = get_values(driver, 'Asking Price:')
        revenue = get_values(driver, 'Revenue')
        cash_flow = get_values(driver, 'Cash flow')
        ebitda = get_values(driver, 'EBITDA')
        established = get_values(driver, 'Established')
        push_to_database(listing_type, name, location, industry,
                         asking_price, revenue, cash_flow, ebitda, established)
    except:
        return


def crawl_data_with_soup(driver, url, listing_type, industry):
    try:
        driver.get("view-source:"+url)
        soup = BeautifulSoup(driver.find_element(
            By.TAG_NAME, "html").text, 'html.parser')
    except:
        return

    try:
        name = soup.find("h1").text.replace("\n", "").replace("  ", "")
        location = soup.select_one('h2.gray').text.replace(
            "\n", "").replace("  ", "")
        asking_price = get_values(soup, 'Asking Price:')
        revenue = get_values(soup, 'Revenue')
        cash_flow = get_values(soup, 'Cash flow')
        ebitda = get_values(soup, 'EBITDA')
        established = get_values(soup, 'Established')
    except:
        return
    conti = 1
    while(conti):
        try:
            push_to_database(listing_type, name, location, industry,
                             asking_price, revenue, cash_flow, ebitda, established)
            conti = 0
        except Exception as e:
            print(str(e))
            if(str(e).find("database is locked") == -1):
                return
            print("Disconnected with database!")
            time.sleep(2)


def delete_second_link(l):
    cmd = "DELETE FROM data where link = '"+str(l)+"'"
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(cmd)
        conn.commit()


def get_records_left_in_database():
    cmd = "SELECT count(*) FROM data;"
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute(cmd)
        conn.commit()
    for i in cursor:
        result = i[0]
        break
    print(result, " records left.")
    if(result == 0):
        return False
    return True


def crawl(driver, second_links):
    try:
        link = second_links[random.randint(0, len(second_links))]

        crawl_data_with_soup(driver, link[0], link[1], link[2])
        # delete this "link to second page" in database
        this_link_is_used(link[0])
        # 
        second_links.remove(link)
    except:
        pass


def this_link_is_used(l):
    cmd = "update data set status = 1 where link = '"+str(l)+"'"
    conti = 1
    while(conti):
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                conn.execute(cmd)
            conti = 0
        except Exception as e:
            print(str(e))
            if(str(e).find("database is locked") == -1):
                return
            print("Disconnected with database!")
            time.sleep(2)
    conn.commit()


def process():
    cmd = "SELECT link, [Listing type], industry FROM data where status = 0;"
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute(cmd)
        conn.commit()
    second_links = []
    for i in cursor:
        second_links.append(i)

    driver = initDriver()
    # range(HOW_MANY_THREAD_DO_YOU_NEED)

    while(get_records_left_in_database()):
        crawl(driver, second_links)
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
    driver = initDriver()
    # crawl links to second pages
    for i in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
        get_all_link(driver, i[0], i[1], i[2])
    # crawl data in second pages
    crawl_with_beautifulSoup()

    input("Successful!")

    # 1. open browser and scrape all links to second pages
    # - open browser
    # - go to the website
    # - chose some options
    # - repeat: get all links 
    #           save all links into database
    #           click next page
    #   end: all options are chosen
    # 2. open each "links to second pages" and scrape data
    # - read all links inside the database
    # - repeat:
    #           go to the link
    #           scrape data (select element and get attribute of that)
    #           delete this link in the database
    #   end: all links in database is removed
