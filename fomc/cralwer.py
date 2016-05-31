# coding=utf-8

import datetime
import json
import os
import re
import time
import traceback
import urllib.request
from collections import defaultdict
from datetime import datetime
from os.path import exists

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains

__author__ = 'ChaoMing'

shop_root_url = "http://waimai.baidu.com/waimai/shop/"
comment_root_url = "http://waimai.baidu.com/shopui/?qt=shopcomment&shop_id="
pattern = re.compile(r"\s+")
crawl_day = datetime.now().strftime("%Y-%m-%d")


# 第一部分工作：得到餐厅的URL和搜索结果列表
def get_list():
    urls, filename, line_index = {}, crawl_day + "_shop_urls.txt", 1
    with open("files/waimai/2015-11-1_baiduwaimai_urls.txt", "r", encoding="gbk") as f:
        for line in f:
            url, search_address = pattern.split(line.strip())

            browser = webdriver.Firefox()
            browser.get(url)
            browser.maximize_window()
            for i in range(10):
                browser.find_element_by_id("baiducopy").click()
                time.sleep(2)
            page_source = browser.page_source
            browser.quit()

            soup = BeautifulSoup(page_source, "html.parser")
            if soup.find("ul", class_="shopcards-list"):
                for li in soup.find("ul", class_="shopcards-list").find_all("li", class_="list-item"):
                    new_key = li.get("class")[2][4:]
                    address_id = str(line_index)  # search_address_id(search_address)
                    if new_key in urls.keys():
                        urls[new_key] += "," + address_id
                    else:
                        urls[new_key] = address_id

            line_index += 1

            with open("files/waimai/" + filename, "w") as f2:
                for key in urls.keys():
                    f2.write(key + "\t" + urls[key] + "\n")


# 第二部分工作：获取餐厅信息、菜品信息、以及评论信息
def get_data():
    filename, dining_id = crawl_day + "_shop_urls.txt", 1
    with open("files/waimai/" + filename, "r") as f:
        for line in f:
            url_num, search_address = pattern.split(line.strip())
            html_content = get_html(shop_root_url + url_num).replace("&nbsp;", "")
            soup = BeautifulSoup(html_content, "html.parser")

            # 得到餐厅信息
            the_url = shop_root_url + url_num
            div = soup.find("div", class_="b-info fl")
            if div is not None:  # 第一种HTML编排方式
                path = "files/waimai/" + crawl_day + "_shops_info.json"
                get_shop_info(soup, the_url, search_address, path, dining_id)
            else:  # 第二种HTML编排方式
                path = "files/waimai/" + crawl_day + "_shops_info2.json"
                get_shop_info2(soup, the_url, search_address, path, dining_id)

            # 得到餐厅菜品信息
            if soup.find("section", class_="menu-list") is not None:
                get_food_info(soup, dining_id)
            else:
                get_food_info2(shop_root_url + url_num, dining_id)

            # 得到餐厅评价信息
            get_comment_info(comment_root_url + url_num, dining_id)

            dining_id += 1


def search_address_id(search_address):
    # book = xlrd.open_workbook("files/waimai/search_address.xls")
    # sh = book.sheet_by_index(0)
    # for i in range(sh.nrows):
    #     if search_address == str(sh.cell_value(rowx=i, colx=0)).strip():
    #         return str(int(sh.cell_value(rowx=i, colx=1))).strip()
    with open("files/waimai/2015-11-1_baiduwaimai_urls.txt", "r") as f:
        i, found = 1, False
        for line in f:
            splits = pattern.split(line.strip())
            if search_address == splits[1]:
                found = True
                return str(i)
            i += 1
        if not found:
            return "0"


def write_json(path, a_dict):
    if not isinstance(a_dict, dict):
        print("写入文件错误，需要传入一个字典类型变量")
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(a_dict, ensure_ascii=False, separators=(',', ":")) + "\n")


def get_html(a_url):
    headers = {'Connection': 'Keep-Alive', 'Accept': 'text/html, application/xhtml+xml, */*',
               'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'}
    request = urllib.request.Request(a_url, headers=headers)
    return urllib.request.urlopen(request).read().decode("utf-8", errors="ignore")


def get_shop_info(soup, a_url, search_address_ids, path, dining_id):
    try:
        # URL、爬取时间、搜索所用地址
        shop_info_dict = {"url": a_url, "search_address_ids": search_address_ids,
                          "crawl_day": crawl_day, "ID": dining_id}

        # 餐厅菜品分类
        categories = {}
        for a in soup.find("section", class_='menu-filter clearfix').find_all("a", class_="filter-item"):
            key = re.compile("\d+").search(a.em.string.strip()).group()
            value = a.span.get("title")
            categories[key] = value
        shop_info_dict["categories"] = categories

        # 餐厅名、是否百度配送
        div = soup.find("div", class_="b-info fl")
        shop_info_dict["restaurant"] = div.find("div", class_="all-show").h2.string.strip()
        try:
            a = div.find("div", class_="all-show").span.string
            shop_info_dict["baidu_delivery"] = True
        except AttributeError:
            shop_info_dict["baidu_delivery"] = False
            # traceback.print_exc()

        # 餐厅类型、总体评分、接单时间、商户地址
        dls = div.find_all("dl")
        shop_info_dict["dining_type"] = dls[0].dt.string.strip()
        shop_info_dict["dining_grade"] = dls[0].dd.get_text(strip=True)
        shop_info_dict["receiving_time"] = dls[1].dd.span.string.strip()
        shop_info_dict["address"] = dls[2].dd.string.strip()

        # 餐厅详细评分
        table = soup.find("div", class_="overall").find("table")
        tags = ["five", "four", "three", "two", "one"]
        detail_grades = {}
        for i, tr in enumerate(table.find_all("tr")):
            detail_grades[tags[i]] = tr.find_all("td")[-1].string.strip()
        shop_info_dict["detail_grades"] = detail_grades

        # 餐厅配送费
        shop_info_dict["delivery_fee"] = soup.find("div", class_="b-cost fr").strong.string.string.strip()
        # 餐厅起送价
        shop_info_dict["play_price"] = soup.find("div", class_="b-price fr").strong.string.string.strip()
        # 餐厅平均送达时间
        try:
            shop_info_dict["average_time"] = soup.find("div", class_="b-totime fr").strong.string.string.strip()
        except AttributeError:
            shop_info_dict["average_time"] = ""
        # 商家通知
        try:
            shop_info_dict["announcement"] = soup.find("div", class_="annouce").get_text(strip=True)
        except AttributeError:
            shop_info_dict["announcement"] = ""

        # 支付信息
        try:
            shop_info_dict["premium_notice"] = list(soup.find("ul", id="premium-notice").stripped_strings)
        except AttributeError:
            shop_info_dict["premium_notice"] = ""

        # 商家公告
        shop_info_dict["shop_notice"] = soup.find("p", class_='notice-desc').string.strip()

        # 菜品文件、评价文件
        shop_info_dict["food_filename"] = crawl_day + "_" + str(dining_id) + "_foods.json"
        shop_info_dict["comment_filename"] = crawl_day + "_" + str(dining_id) + "_comments.json"

        write_json(path, shop_info_dict)
        print("爬取完第", dining_id, "个餐厅的信息。")
    except:
        traceback.print_exc()
        print(a_url, end="\n\n\n")


def get_shop_info2(soup, a_url, search_address_ids, path, dining_id):
    try:
        # URL、爬取时间、搜索所用地址
        shop_info_dict = {"url": a_url, "search_address_ids": search_address_ids, "crawl_day": crawl_day, "ID": dining_id}

        # 餐厅名称
        shop_info_dict["restaurant"] = soup.find("div", class_="b-title").h2.string.strip()

        # 餐厅菜品分类
        shop_info_dict["categories"] = {}

        # 配送时间、起送价、配送费
        divs = soup.find("div", class_="shop-time").find_all("strong", class_="b-num")
        shop_info_dict["average_time"] = ""
        if len(divs) == 3:
            shop_info_dict["average_time"] = divs[0].string.strip()
        shop_info_dict["play_price"] = divs[-2].string.strip()
        shop_info_dict["delivery_fee"] = divs[-1].string.strip()

        # 总体评价、营业时间、地址
        dls = soup.find("div", class_="b-info").find_all("dl")
        shop_info_dict["dining_grade"] = dls[0].get_text("|", strip=True).split("|")[-1]
        shop_info_dict["receiving_time"] = list(dls[1].stripped_strings)[1]
        shop_info_dict["address"] = list(dls[2].stripped_strings)[-1]

        # 支付信息
        try:
            shop_info_dict["premium_notice"] = list(soup.find("div", class_="premium-notice").stripped_strings)
        except AttributeError:
            shop_info_dict["premium_notice"] = ""

        # 商家公告
        shop_info_dict["shop_notice"] = soup.find("p", class_='notice-desc').string.strip()

        # 菜品文件、评价文件
        shop_info_dict["food_filename"] = crawl_day + "_" + str(dining_id) + "_foods.json"
        shop_info_dict["comment_filename"] = crawl_day + "_" + str(dining_id) + "_comments.json"

        write_json(path, shop_info_dict)
        print("爬取完第", dining_id, "个餐厅的信息。")
    except:
        traceback.print_exc()
        print(a_url, end="\n\n\n")


def get_food_info(soup, dining_id):
    for i, a_list in enumerate(soup.find("section", class_="menu-list").find_all("div", class_="list-wrap")):
        # 餐厅分类
        category = a_list.find("div", class_="list-status").get_text(strip=True)
        if category == "热销菜品":
            continue
        for li in a_list.find_all("li", class_="list-item"):
            try:
                food_info = {"dining_id": dining_id, "category": category}
                # 菜品名、菜品提示
                h3 = li.find("div", class_="info fl").h3
                food_info["name"] = h3.string.strip()
                try:
                    food_info["tips"] = h3.get("data-content").strip()
                except AttributeError:
                    food_info["tips"] = ""
                # 推荐数、销售量、价格
                spans = li.find("div", class_="info-desc").find_all("span", class_="sales-count")
                food_info["recommand"] = re.compile("\d+").search(spans[0].string.strip()).group()
                food_info["sale_amount"] = re.compile("\d+").search(spans[1].string.strip()).group()
                try:
                    food_info["price"] = re.compile("\d+"). \
                        search(li.find("div", class_="m-price").get_text(strip=True)).group()
                except AttributeError:
                    food_info["price"] = re.compile("\d+"). \
                        search(li.find("div", class_="m-break").get_text(strip=True)).group()
                write_json("files/waimai/" + crawl_day + "_" + str(dining_id) + "_foods.json", food_info)
            except:
                print("餐厅id", dining_id)
                traceback.print_exc()
    print("爬完第", dining_id, "个餐厅的菜品信息。")


def get_food_info2(a_url, dining_id):
    browser = webdriver.Firefox()
    browser.get(a_url)
    browser.maximize_window()
    while True:
        page_source = browser.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        for li in soup.find("section", class_="market-list").find_all("li"):
            try:
                food_info = {"dining_id": dining_id, "category": ""}
                # 菜品名、菜品提示
                h3 = li.find("div", class_="info").h3
                food_info["name"] = h3.string.strip()
                try:
                    food_info["tips"] = h3.get("data-content").strip()
                except AttributeError:
                    food_info["tips"] = ""
                # 推荐数、销售量、价格
                spans = li.find("div", class_="info-desc").find_all("span", class_="sales-count")
                food_info["recommand"] = re.compile("\d+").search(spans[0].string.strip()).group()
                food_info["sale_amount"] = re.compile("\d+").search(spans[1].string.strip()).group()
                try:
                    food_info["price"] = re.compile("\d+"). \
                        search(li.find("div", class_="m-price").get_text(strip=True)).group()
                except AttributeError:
                    food_info["price"] = re.compile("\d+"). \
                        search(li.find("div", class_="m-break").get_text(strip=True)).group()

                write_json("files/waimai/" + crawl_day + "_" + str(dining_id) + "_foods.json", food_info)
            except:
                print("餐厅id", dining_id)
                traceback.print_exc()
        try:
            the_next = browser.find_element_by_xpath(
                "//div[@class='pagination']//a[@class='mod-page-item mod-page-item-next']")
            the_next.click()
            time.sleep(2)
        except NoSuchElementException:
            break
    browser.quit()
    print("爬完第", dining_id, "个餐厅的菜品信息。")


def get_comment_info(a_url, dining_id):
    browser = webdriver.Firefox()
    browser.get(a_url)
    browser.maximize_window()
    while True:
        footer = browser.find_element_by_xpath("//div[@class='footer-items']")
        for i in range(2):
            ActionChains(browser).move_to_element(footer).perform()
            time.sleep(1)

        page_source = browser.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        div = soup.find("section", "comment-list").find("div", "comment-con")
        if div.find("div", class_="no-result") is not None:
            break
        else:
            for a_div in div.find_all("div", class_="list clearfix"):
                try:
                    comment_info = {"dining_id": dining_id}
                    top_sec = a_div.find("div", class_="top-section").get_text("|", strip=True).split("|")
                    comment_info["user_name"] = top_sec[0]  # a_div.find("span", class_="user-name").string.strip()
                    comment_info["mark"] = top_sec[1]
                    comment_info["delivery_time"] = top_sec[
                        2]  # a_div.find("span", class_="delivery-time").string.strip()
                    comment_info["comment_time"] = top_sec[3]  # a_div.find("span", class_="fr").string.strip()
                    comment_info["content"] = a_div.find("div", class_="mid-section").get_text(strip=True)
                    if a_div.find("div", class_="btm-section") is not None:
                        comment_info["recommand"] = a_div.find("div", class_="btm-section").get_text("|",
                                                                                                     strip=True).split(
                            "|")[1:]
                    else:
                        comment_info["recommand"] = []

                    write_json("files/waimai/" + crawl_day + "_" + str(dining_id) + "_comments.json", comment_info)
                except:
                    print("餐厅id", dining_id)
                    traceback.print_exc()
        try:
            the_next = browser.find_element_by_xpath(
                "//div[@class='pagination']//a[@class='mod-page-item mod-page-item-next']")
            the_next.click()
            time.sleep(2)
        except NoSuchElementException:
            break
    browser.quit()
    print("爬完第", dining_id, "个餐厅的评论信息。")


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


def get_pos_and_neg_corpus():
    """
    get the positive and negative f_corpus according to the command mark
    """

    def string_is_too_short(a_string):
        """
        judge if the f_corpus is too short or the chinese characters are few
        if True, write to the abandoned file
        :param a_string: a f_corpus
        :return: True or False
        """
        if len(a_string) < 5:
            write_into_rubbish_corpus_file("Too short:", a_string)
            return True
        if len(re.findall(r'[\u4e00-\u9fa5]', a_string)) <= len(a_string) * 0.4:
            write_into_rubbish_corpus_file("Few words:", a_string)
            return True
        return False

    def string_is_numeric(a_string):
        """
        judge if the f_corpus's characters are all or almost numbers
        if True, write to the abandoned file
        :param a_string: a f_corpus
        :return: True or False
        """
        match = (re.match(r'\d+', a_string))
        if match is not None and len(match.group()) >= len(a_string) * 0.75:
            write_into_rubbish_corpus_file("Is numeric:", a_string)
            return True
        return False

    def string_is_english(a_string):
        """
        judge if the f_corpus's characters are all English
        if True, write to the abandoned file
        :param a_string: a f_corpus
        :return: True or False
        """
        match = re.match(r"[a-zA-Z]+", a_string)
        if match is not None and len(match.group()) >= len(a_string) * 0.75:
            write_into_rubbish_corpus_file("Is english:", a_string)
            return True
        return False

    def string_is_word_repeat(a_string):
        """
        check if the f_corpus is always the repeat word
        :param a_string: a f_corpus
        :return: True or False
        """
        repeat_words, length = [], 0
        for word in a_string:
            if a_string.count(word) >= 4 and word not in repeat_words:
                repeat_words.append(word)
                length += content.count(word)
        if length > len(content) / 2:
            write_into_rubbish_corpus_file("Word repeat:", a_string)
            return True
        return False

    def string_is_sentence_repeat(filepath, a_string):
        """
        judge if the string is the same as the another string in the lines
        :param filepath: file path
        :param a_string: a f_corpus
        :return: True or False
        """
        repeat = False
        with open(filepath, "r", encoding="utf-8") as check_f:
            for a_line in check_f:
                if a_line.strip() in a_string and len(a_line.strip()) * 2 >= len(a_string):
                    repeat = True
                if a_string in a_line.strip() and len(a_string) * 2 >= len(a_line.strip()):
                    repeat = True
                if repeat:
                    write_into_rubbish_corpus_file("Sentence repeat:", a_string)
                    write_into_rubbish_corpus_file("Sentence repeat:", a_line.strip())
                    break
        return repeat

    def write_into_rubbish_corpus_file(type_string, a_string):
        """
        write the f_corpus into the rubbish f_corpus file
        :param type_string: the rubbish type
        :param a_string: a f_corpus
        """
        with open(abandoned_filepath, "a", encoding="utf-8") as abandoned_f:
            abandoned_f.write(type_string + "\n\t" + str(a_string) + "\n")

    def write_into_corpus_file(filepath, a_string):
        """
        write the f_corpus into the corresponding file if there is no repeat,
        otherwise, write it into the abandoned file
        :param filepath: file path
        :param a_string: a f_corpus
        """
        repeat = string_is_sentence_repeat(filepath, a_string)
        if not repeat:
            with open(filepath, "a", encoding="utf-8") as final_corpus_f:
                final_corpus_f.write(str(a_string) + "\n")

    waimai_corpus_root_path = "waimai/2015-11-05/"
    abandoned_filepath = "waimai/abandoned/abandoned_corpus.txt"
    positive_filepath = "waimai/pos/positive_corpus_v2.txt"
    negative_filepath = "waimai/neg/negative_corpus_v2.txt"
    four_mark_filepath = "waimai/handle/four_mark_corpus.txt"
    runout_filepath = "f_runout/get_waimai_pos_and_neg_corpus.txt"

    open(abandoned_filepath, "w", encoding="utf-8")
    open(positive_filepath, "w", encoding="utf-8")
    open(negative_filepath, "w", encoding="utf-8")
    open(four_mark_filepath, "w", encoding="utf-8")

    start_time = time.clock()
    total_index, useful_index = 0, 0
    for filename in os.listdir(waimai_corpus_root_path):
        if "comment" in filename:
            with open(waimai_corpus_root_path + filename, "r", encoding="utf-8") as corpus_f:
                for line in corpus_f:
                    total_index += 1
                    print("finish the number of %d f_corpus in total." % total_index)

                    a_comment = json.loads(line.strip())
                    content = ",".join(re.split(r"\s+", a_comment["content"]))

                    if string_is_too_short(content):
                        continue
                    if string_is_numeric(content):
                        continue
                    if string_is_english(content):
                        continue
                    if string_is_word_repeat(content):
                        continue

                    try:
                        mark = int("".join(re.findall("\d+", a_comment["mark"])))

                        if mark == 5:
                            write_into_corpus_file(positive_filepath, content)

                        if mark == 4:
                            write_into_corpus_file(four_mark_filepath, content)

                        if mark <= 3:
                            write_into_corpus_file(negative_filepath, content)

                        useful_index += 1
                        print("finish the number of %d f_corpus useful." % useful_index)
                    except ValueError:
                        write_into_rubbish_corpus_file("ValueError:", a_comment)

    end_time = time.clock()
    with open(runout_filepath, "w", encoding="utf-8") as runout_f:
        runout_f.write("total f_corpus: %d\n" % total_index)
        runout_f.write("useful f_corpus: %d\n" % useful_index)
        runout_f.write("time used: " + str(end_time - start_time))


def test1():
    # get_list()
    get_data()
    # get_food_info2("http://waimai.baidu.com/shopui/upc/shopview?shop_id=1453983291", 50)
    # get_food_info2("http://waimai.baidu.com/shopui/upc/shopview?shop_id=1432894748", 51)
    # get_food_info2("http://waimai.baidu.com/shopui/upc/shopview?shop_id=1486968978", 52)
    # get_comment_info("http://waimai.baidu.com/shopui/?qt=shopcomment&shop_id=1437829794", 1)
    # get_comment_info("http://waimai.baidu.com/shopui/shopcomment?shop_id=1432894748", 2)
    # get_comment_info("http://waimai.baidu.com/shopui/?qt=shopcomment&shop_id=1427545914", 3)


def test2():
    crawler = BaiDuWaiMaiCrawler()
    crawler.test()


if __name__ == "__main__":
    pass
    # test1()
    # test2()
