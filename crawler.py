import re
import time
from datetime import datetime
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import traceback
import json
from os.path import exists
from collections import defaultdict


class BaiDuWaiMaiCrawler:
    def __init__(self):
        self.comment_root_url = "http://waimai.baidu.com/shopui/?qt=shopcomment&shop_id="
        self.comment_root_path = "files/baiduwaimai_comments-%s.json" % datetime.now().strftime("%Y-%m-%d")
        self.browser = Firefox()
        self.ids = defaultdict(list)
        self.crawled_ids = []
        self.crawled_id_filepath = "files/crawled_ids.txt"
        self.get_crawled_ids()

    def __del__(self):
        self.browser.quit()

    def get_crawled_ids(self):
        if exists(self.crawled_id_filepath):
            with open(self.crawled_id_filepath, encoding="utf-8") as f:
                for line in f:
                    self.crawled_ids.append(line.strip())

    def record_crawled_id(self, shop_id):
        with open(self.crawled_id_filepath, mode="a", encoding="utf-8") as f:
            f.write("%s\n" % shop_id)

    @staticmethod
    def get_address_urls_from_file():
        urls = []
        pattern = re.compile("\s+")
        with open("files/baiduwaimai_address_urls.txt") as f:
            for line in f:
                results = pattern.split(line.strip())
                if len(results) >= 2:
                    urls.append(results[0])
        print("从文件内得到所有地址的url")
        return urls

    def get_shop_ids_from_file(self, filepath, encoding="utf-8"):
        pattern = re.compile("\s+")
        with open(filepath, encoding=encoding) as f:
            for line in f:
                results = pattern.split(line.strip())
                if len(results) >= 2:
                    self.ids[results[0]] = results[1].split(",")

    def get_shop_ids_from_net(self):
        address_urls = self.get_address_urls_from_file()
        for index, url in enumerate(address_urls):
            self.shop_urls_at_a_address(url, index)

    def shop_urls_at_a_address(self, url, line_index):
        self.browser.get(url)
        self.browser.maximize_window()
        for i in range(10):
            self.browser.find_element_by_id("baiducopy").click()
            time.sleep(2)
        page_source = self.browser.page_source
        # self.browser.close()

        soup = BeautifulSoup(page_source, "html.parser")
        if soup.find("ul", class_="shopcards-list"):
            for li in soup.find("ul", class_="shopcards-list").find_all("li", class_="list-item"):
                key = li.get("class")[2][4:]
                address_id = str(line_index)
                self.ids[key].append(address_id)

    def get_comments_in_one_shop(self, shop_id):
        self.browser.get("%s%s" % (self.comment_root_url, shop_id))
        self.browser.maximize_window()
        while True:
            footer = self.browser.find_element_by_xpath("//div[@class='footer-items']")
            for i in range(2):
                ActionChains(self.browser).move_to_element(footer).perform()
                time.sleep(1)

            page_source = self.browser.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            div = soup.find("section", "comment-list").find("div", "comment-con")
            if div.find("div", class_="no-result") is not None:
                break
            else:
                for a_div in div.find_all("div", class_="list clearfix"):
                    self.get_one_comment(a_div, shop_id)
            try:
                the_next = self.browser.find_element_by_xpath(
                    "//div[@class='pagination']//a[@class='mod-page-item mod-page-item-next']")
                the_next.click()
                time.sleep(2)
            except NoSuchElementException:
                break
        # self.browser.close()
        print("爬完ID为 '", shop_id, "' 的餐厅的评论信息。")
        self.record_crawled_id(shop_id)
        self.crawled_ids.append(shop_id)

    def get_one_comment(self, div, shop_id):
        try:
            comment_info = {"shop_id": shop_id}
            top_sec = div.find("div", class_="top-section").get_text("|", strip=True).split("|")
            comment_info["user_name"] = top_sec[0]  # a_div.find("span", class_="user-name").string.strip()
            comment_info["mark"] = top_sec[1][:-1]
            comment_info["delivery_time"] = top_sec[2]  # a_div.find("span", class_="delivery-time").string.strip()
            comment_info["comment_time"] = top_sec[3]  # a_div.find("span", class_="fr").string.strip()
            comment_info["content"] = div.find("div", class_="mid-section").get_text(strip=True)
            if div.find("div", class_="btm-section") is not None:
                comment_info["recommend"] = div.find("div", class_="btm-section").get_text(
                    "|", strip=True).split("|")[1:]
            else:
                comment_info["recommend"] = []
            with open(self.comment_root_path, mode="a", encoding="utf-8") as f:
                a_json = json.dumps(comment_info, ensure_ascii=False, separators=(",", ":"))
                f.write("%s\n" % a_json)
        except:
            print("id为'%s'的餐厅有Bug，请检查。", shop_id)
            traceback.print_exc()

    def get_all_shop_comments(self):
        for shop_id in self.ids.keys():
            self.get_comments_in_one_shop(shop_id)

    def test(self):
        self.get_shop_ids_from_file("files/baiduwaimai_shop_urls.txt")
        self.get_all_shop_comments()

if __name__ == "__main__":
    crawler = BaiDuWaiMaiCrawler()
    crawler.test()



