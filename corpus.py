import os
import re
import jieba


class MovieCorpus:
    def __init__(self):
        # get the root path
        root_path = os.path.dirname(os.path.abspath(__file__))
        pos_root_path = os.path.join(root_path, "corpus_/movie/pos/")
        neg_root_path = os.path.join(root_path, "corpus_/movie/neg/")

        pattern = re.compile(r"([\w'\"]+|[.,!?;])")

        # load all the positive article and its length
        self.pos_doc_list = []
        for filename in os.listdir(pos_root_path):
            word_list = pattern.findall(open(os.path.join(pos_root_path, filename),
                                             errors="ignore", encoding="utf-8").read())
            self.pos_doc_list.append(word_list)
        self.pos_doc_length = len(self.pos_doc_list)

        # load all the negative article and its length
        self.neg_doc_list = []
        for filename in os.listdir(neg_root_path):
            word_list = pattern.findall(open(os.path.join(neg_root_path, filename),
                                             errors="ignore", encoding="utf-8").read())
            self.neg_doc_list.append(word_list)
        self.neg_doc_length = len(self.neg_doc_list)

        # define the variable about train number
        self.pos_train_num = 0
        self.pos_test_num = 0
        self.neg_train_num = 0
        self.neg_test_num = 0

        runout_content = "You are using the movie corpus_ version 0.9.\n"
        runout_content += "There are total %d positive and %d negative corpus_." % \
                          (self.pos_doc_length, self.neg_doc_length)
        print(runout_content)

    def get_all_corpus(self):
        the_doc_list = self.pos_doc_list + self.neg_doc_list
        the_doc_labels = [1] * self.pos_doc_length + [0] * self.neg_doc_length
        return the_doc_list, the_doc_labels

    def get_train_corpus(self, pos_num, neg_num):
        self.pos_train_num = pos_num
        self.neg_train_num = neg_num

        assert self.pos_doc_length >= self.pos_test_num + self.pos_train_num
        assert self.neg_doc_length >= self.neg_test_num + self.neg_train_num

        train_data = self.pos_doc_list[:pos_num] + self.neg_doc_list[:neg_num]
        train_data_labels = [1] * pos_num + [0] * neg_num
        return train_data, train_data_labels

    def get_test_corpus(self, pos_num, neg_num):
        self.pos_test_num = pos_num
        self.neg_test_num = neg_num

        assert self.pos_doc_length >= self.pos_test_num + self.pos_train_num
        assert self.neg_doc_length >= self.neg_test_num + self.neg_train_num

        test_data = self.pos_doc_list[self.pos_train_num: self.pos_train_num + pos_num] + \
            self.neg_doc_list[self.neg_test_num: self.neg_test_num + neg_num]
        test_data_labels = [1] * pos_num + [0] * neg_num

        return test_data, test_data_labels


class WaimaiCorpus:
    def __init__(self):
        # load the jieba user.dict
        root_path = os.path.dirname(os.path.abspath(__file__))
        jieba.load_userdict(os.path.join(root_path, "dict/user.dict"))

        # get the positive corpus_ and length
        self.pos_doc_list = []
        with open(os.path.join(root_path, "corpus_/waimai/positive_corpus_v1.txt"), encoding="utf-8") as pos_f:
            for line in pos_f:
                # self.pos_doc_list.append(list(set(jieba.lcut(line.strip()))))
                self.pos_doc_list.append(jieba.lcut(line.strip()))
        self.pos_doc_length = len(self.pos_doc_list)

        # get the negative corpus_ and length
        self.neg_doc_list = []
        with open(os.path.join(root_path, "corpus_/waimai/negative_corpus_v1.txt"), encoding="utf-8") as pos_f:
            for line in pos_f:
                # self.neg_doc_list.append(list(set(jieba.lcut(line.strip()))))
                self.neg_doc_list.append(jieba.lcut(line.strip()))
        self.neg_doc_length = len(self.neg_doc_list)

        # define the variable about train number
        self.pos_train_num = 0
        self.neg_train_num = 0
        self.pos_test_num = 0
        self.neg_test_num = 0

        runout_content = "You are using the waimai corpus_ version 1.0.\n"
        runout_content += "There are total %d positive and %d negative corpus_." % \
                          (self.pos_doc_length, self.neg_doc_length)
        print(runout_content)

    def get_all_corpus(self):
        the_doc_list = self.pos_doc_list + self.neg_doc_list
        the_doc_labels = [1] * self.pos_doc_length + [0] * self.neg_doc_length
        return the_doc_list, the_doc_labels

    def get_train_corpus(self, pos_num, neg_num):
        self.pos_train_num = pos_num
        self.neg_train_num = neg_num

        assert self.pos_doc_length >= self.pos_test_num + self.pos_train_num
        assert self.neg_doc_length >= self.neg_test_num + self.neg_train_num

        train_data = self.pos_doc_list[:pos_num] + self.neg_doc_list[:neg_num]
        train_data_labels = [1] * pos_num + [0] * neg_num
        return train_data, train_data_labels

    def get_test_corpus(self, pos_num, neg_num):
        self.pos_test_num = pos_num
        self.neg_test_num = neg_num

        assert self.pos_doc_length >= self.pos_test_num + self.pos_train_num
        assert self.neg_doc_length >= self.neg_test_num + self.neg_train_num

        test_data = self.pos_doc_list[self.pos_train_num: self.pos_train_num + pos_num] + \
            self.neg_doc_list[self.neg_test_num: self.neg_test_num + neg_num]
        test_data_labels = [1] * pos_num + [0] * neg_num

        return test_data, test_data_labels
