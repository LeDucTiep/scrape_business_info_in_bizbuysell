import multiprocessing
import sqlite3
import time
import os
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

# create your own github token when this GH_TOKEN is gone
# https://github.com/SergeyPirogov/webdriver_manager#gh_token
os.environ['GH_TOKEN'] = "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"

DATABASE_PATH = "database.db"

# it will open 4 browsers for scraping data in the second page
HOW_MANY_THREAD_DO_YOU_NEED = 20


def push_to_database(listing_type, name, location, industry, asking_price, revenue, cash_flow, ebitda, established) -> None:
    try:
        cmd = '''insert into results  ([Listing type] ,
                Name,
                Location,
                Industry,
                [Asking Price],
                Revenue,
                [Cash flow],
                EBITDA,
                [Established date]) values  (\'''' + str(listing_type).replace('\r', '').replace("'", "''") + "\', \'"+str(name).replace('\r', '').replace("'", "''")+"\', \'"+str(location).replace('\r', '').replace("'", "''")+"\', \'"+str(industry).replace('\r', '').replace("'", "''")+"\', \'"+str(asking_price).replace('\r', '').replace("'", "''")+"\', \'"+str(revenue).replace('\r', '').replace("'", "''")+"\', \'"+str(cash_flow).replace('\r', '').replace("'", "''")+"\', \'"+str(ebitda).replace('\r', '').replace("'", "''")+"\', \'"+str(established).replace('\r', '').replace("'", "''")+"\')"
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute(cmd)
            conn.commit()
    except Exception as e:
        if(str(e).find("UNIQUE") != -1):
            pass
        else:
            print(str(e))
            time.sleep(1)
            push_to_database(listing_type, name, location, industry,
                             asking_price, revenue, cash_flow, ebitda, established)


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


def this_link_is_used(l):
    cmd = "update data set status = 1 where link = '"+str(l)+"'"
    conti = 1
    while(conti):
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                conn.execute(cmd)
                conn.commit()
            conti = 0
        except Exception as e:
            print(str(e))
            if(str(e).find("database is locked") == -1):
                return
            print("Disconnected with database!")
            time.sleep(2)


class FirstPage:
    def initDriver(self, IS_HEADLESS=False) -> webdriver:
        options = Options()
        # options.add_argument("--disable-blink-features")
        options.add_argument("--start-maximized")
        # options.add_argument("--disable-blink-features=AutomationControlled")
        options.headless = IS_HEADLESS
        # set to 2: disable loading image
        # set to 1: enable ...
        options.set_preference(
            "permissions.default.image", 2)
        self.driver = webdriver.Firefox(service=Service(
            GeckoDriverManager(path="./geckodriver").install()), options=options)

    def crawl_link(self, industry):
        try:
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "h3.title.ng-star-inserted")))
        except:
            pass

        try:
            all_tags = self.driver.execute_script(
                "return document.getElementsByClassName('listing-container')[0].children")
        except:
            return

        for tag in all_tags:
            try:
                url = tag.find_element(By.TAG_NAME, "a").get_attribute('href')
                cmd = "insert into data(link, [Listing type], industry) values ('" + \
                    url+"', '"+self.Listing_type+"', '"+industry+"')"
                with sqlite3.connect(DATABASE_PATH) as conn:
                    conn.execute(cmd)
                    conn.commit()
            except:
                pass

    def close_dialog(self):
        self.click_no_thank()
        self.click_close_menu()

    def wait_until_Listing_type_displayed(self):
        try:
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.franchise-op")))
        except:
            pass

    def click_listing_type_button(self):
        try:
            self.driver.execute_script(
                "document.getElementsByClassName('btn filter-bar listing-types-button listing-type')[0].click()")
        except:
            pass

    def click_industries_button(self):
        try:
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "hlSelectCategories"))).click()
        except:
            pass

    def click_for_more_industries(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.all-industries-option.ng-tns-c6-3.ng-star-inserted"))).click()
        except:
            self.click_industries_button()
            self.click_for_more_industries()

    def get_all_link(self, Established_business, Startups, Asset_sales):
        Listing_type = ''
        self.driver.get(r'https://www.bizbuysell.com/businesses-for-sale/')

        # click listing-types-button
        self.click_listing_type_button()
        self.wait_until_Listing_type_displayed()

        # click "Established business,..." box
        if(Established_business):
            Listing_type += "Established business, "
            self.driver.execute_script(
                'document.getElementsByTagName("input")[0].click()')
        if(Asset_sales):
            Listing_type += "Asset sales, "
            self.driver.execute_script(
                'document.getElementsByTagName("input")[1].click()')
        if(Startups):
            Listing_type += "Startups, "
            self.driver.execute_script(
                'document.getElementsByTagName("input")[3].click()')

        # "Established business, Startups" = "Established business, Startups, " (https://www.w3schools.com/python/python_strings_slicing.asp)
        Listing_type = Listing_type[:-2]

        self.click_listing_type_button()

        industries_length = 19
        for index_of_industries in range(industries_length):
            self.close_dialog()
            # try:
            self.driver.execute_script(
                "window.scrollTo(0, 0);")
            self.close_dialog()
            self.click_industries_button()
            # except:
            #     self.close_dialog()
            # try:
            self.close_dialog()
            self.click_for_more_industries()
            time.sleep(1)
            self.close_dialog()

            # clear all button clicked
            self.driver.execute_script(
                "document.getElementsByClassName('btn filter cta inverse cancel')[0].click()")
            time.sleep(1)
            # click industry type
            industries_tag = self.driver.find_elements(By.TAG_NAME, "td")
            industries_tag[index_of_industries].click()

            industries_length = len(industries_tag)
            industry = industries_tag[index_of_industries].text
            time.sleep(1)
            self.close_dialog()
            # Click "apply"
            self.driver.execute_script(
                "document.getElementsByClassName('btn filter cta')[0].click()")

            self.close_dialog()

            self.click_industries_button()
            time.sleep(5)
            page = 1
            while(page < 201):
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)
                self.close_dialog()

                self.crawl_link(industry)

                page += 1
                try:
                    self.close_dialog()

                    # next page by click the "next" button
                    WebDriverWait(self.driver, 20).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.bbsPager_next.ng-star-inserted"))).click()

                    # driver.execute_script("document.getElementsByClassName('bbsPager_next ng-star-inserted')[0].click()")
                except Exception as e:
                    if(str(e).find("properties of undefined")):
                        page = 999

    def click_no_thank(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, "button.btn.nt").click()
        except:
            pass

    def click_close_menu(self):
        try:
            self.driver.execute_script(
                "document.getElementsByClassName('close-menu close-chip')[0].click()")
        except:
            pass

    def get_values(self, title):
        for i in range(len(self.driver.find_elements(By.CLASS_NAME, "title"))):
            text = self.driver.find_elements(By.CLASS_NAME, "title")[i].text.lower()
            if(text.find(title.lower()) != -1):
                return self.driver.find_elements(By.CLASS_NAME, "title")[i].find_element(By.XPATH, "..").find_element(By.TAG_NAME, "b").text
        return 'NULL'

    def crawl_data(self, url, listing_type, industry):
        try:
            self.driver.get(url)
        except:
            return
        try:
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "hlWatchListing")))
        except:
            pass

        try:
            name = self.driver.find_element(By.TAG_NAME, 'h1').text
            location = self.driver.find_element(
                By.CSS_SELECTOR, 'h2.gray').text
            asking_price = self.get_values('Asking Price:')
            revenue = self.get_values('Revenue')
            cash_flow = self.get_values('Cash flow')
            ebitda = self.get_values('EBITDA')
            established = self.get_values('Established')
            push_to_database(listing_type, name, location, industry,
                             asking_price, revenue, cash_flow, ebitda, established)
        except:
            return

    def quit(self):
        self.driver.quit()
class SecondPage:
    def crawl(self, link) -> None:
        try:
            if(link == None):
                return None
            self.crawl_data_with_soup(link[0], link[1], link[2])
        except:
            pass

    def get_values(self, soup, title):
        title_tags = soup.select('span.title')
        for i in range(len(title_tags)):
            text = title_tags[i].text.lower()
            if(text.find(title.lower()) != -1):
                return title_tags[i].parent.find('b').text.replace("\n", "").replace("  ", "")
        return 'NULL'

    def crawl_data_with_soup(self, url, listing_type, industry):
        try:
            headers = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
            r = requests.get(url, headers=headers)
            page = r.content
            soup = BeautifulSoup(page, 'html.parser')
        except:
            return
        if(soup.get_text() == '' or soup.get_text().find('Access Denied') != -1):
            print("Blocked!")
            return
        try:
            name = soup.find("h1").text.replace("\n", "").replace("  ", "")
            location = soup.select_one('h2.gray').text.replace(
                "\n", "").replace("  ", "")
            asking_price = self.get_values(soup, 'Asking Price:')
            revenue = self.get_values(soup, 'Revenue')
            cash_flow = self.get_values(soup, 'Cash flow')
            ebitda = self.get_values(soup, 'EBITDA')
            established = self.get_values(soup, 'Established')
        except:
            # with open('error.html', 'w', encoding='utf-8') as f:
            #     f.write(soup.prettify())
            # print("error!")
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

    def get_records_left_in_database(self):
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

    def crawl_with_beautifulSoup(self):
        myDictionary = {}
        count_thread = 0
        while(self.get_records_left_in_database()):
            cmd = "SELECT link, [Listing type], industry FROM data where status = 0 limit 1;"
            with sqlite3.connect("database.db") as conn:
                cursor = conn.execute(cmd)
                conn.commit()
            for i in cursor:
                link = i
                break
            this_link_is_used(link[0])

            myDictionary[count_thread] = multiprocessing.Process(
                target=self.crawl, args=(link,))

            # starting process
            myDictionary[count_thread].start()

            count_thread += 1

            if(len(myDictionary) == HOW_MANY_THREAD_DO_YOU_NEED):
                for d in myDictionary:
                    # wait until process is finished
                    myDictionary[d].join()
                myDictionary = {}


if __name__ == '__main__':
    first_page = FirstPage()
    first_page.initDriver()
    # crawl links to second pages
    for i in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
        first_page.get_all_link(i[0], i[1], i[2])
    first_page.quit()
    # crawl data in second pages
    SecondPage().crawl_with_beautifulSoup()
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
