from tools import get_accuracy
import datetime
from waimai import WaimaiCorpus
from classifiers import KNNClassifier
from feature_extraction import ChiSquare
from multiprocessing import Process


def process(k):
    filepath = ""
    classify_labels = []

    if isinstance(k, list):
        knn = KNNClassifier(train_data, train_labels, k=k, best_words=best_words)
        for data in test_data:
            classify_labels.append(knn.multiple_k_classify(data))

        filepath = "runout/KNNClassifier-pos_train-%d-neg_train-%d-pos_test-%d-neg_test-%d-feature-%d-multiple_k-%s" \
                   "-%s.xls" % (pos_train_num, neg_train_num, pos_test_num, neg_test_num, feature_num,
                                "_".join([str(i) for i in k]), datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    elif isinstance(k, int):
        knn = KNNClassifier(train_data, train_labels, k=k, best_words=best_words)
        for data in test_data:
            classify_labels.append(knn.single_k_classify(data))

        filepath = "runout/KNNClassifier-pos_train-%d-neg_train-%d-pos_test-%d-neg_test-%d-feature-%d-k-%d-" \
                   "%s.xls" % (pos_train_num, neg_train_num, pos_test_num, neg_test_num, feature_num, k,
                               datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    get_accuracy(test_labels, classify_labels, parameters, filepath)

pos_train_num = neg_train_num = 3375
pos_test_num = neg_test_num = 1125
feature_num = 3000
parameters = [pos_train_num, neg_train_num, pos_test_num, neg_test_num, feature_num]

# get the corpus
corpus = WaimaiCorpus()
train_data, train_labels = corpus.get_train_corpus(pos_train_num, neg_train_num)
test_data, test_labels = corpus.get_test_corpus(pos_test_num, neg_test_num)
total_data, total_labels = corpus.get_all_corpus()

# feature extraction
fe = ChiSquare(total_data, total_labels)
best_words = fe.best_words(feature_num)

if __name__ == "__main__":
    k = [1, 3, 5, 7, 9, 11, 13]
    p1 = Process(target=process, args=(k,))
    p1.start()

    k = 1
    p2 = Process(target=process, args=(k,))
    p2.start()

    k = 3
    p3 = Process(target=process, args=(k,))
    p3.start()

    k = 5
    p4 = Process(target=process, args=(k,))
    p4.start()

    k = 7
    p5 = Process(target=process, args=(k,))
    p5.start()

    k = 9
    p6 = Process(target=process, args=(k,))
    p6.start()

    k = 11
    p7 = Process(target=process, args=(k,))
    p7.start()

    k = 13
    p8 = Process(target=process, args=(k,))
    p8.start()
