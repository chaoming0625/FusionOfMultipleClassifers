import re
import os
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
            with open(waimai_corpus_root_path+filename, "r", encoding="utf-8") as corpus_f:
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


if __name__ == "__main__":
    crawler = BaiDuWaiMaiCrawler()
    crawler.test()



