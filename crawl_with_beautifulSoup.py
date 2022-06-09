import multiprocessing
import sqlite3
import time
import requests
from bs4 import BeautifulSoup

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
        with sqlite3.connect("database.db") as conn:
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


def this_link_is_used(l):
    cmd = "update data set status = 1 where link = '"+str(l)+"'"
    conti = 1
    while(conti):
        try:
            with sqlite3.connect("database.db") as conn:
                conn.execute(cmd)
                conn.commit()
            conti = 0
        except Exception as e:
            print(str(e))
            if(str(e).find("database is locked") == -1):
                return
            print("Disconnected with database!")
            time.sleep(2)


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
    SecondPage().crawl_with_beautifulSoup()
    input("Successful!")
