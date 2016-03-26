from tools import get_accuracy
import datetime


def test_dict():
    """
    test the classifier based on Sentiment Dict
    """
    print("DictClassifier")
    print("---" * 45)

    from classifiers import DictClassifier
    ds = DictClassifier()

    # 对一个单句进行情感分析
    # a_sentence = "剁椒鸡蛋好咸,土豆丝很好吃"
    # ds.sentiment_analyse_a_sentence(a_sentence)

    # 对一个文件内语料进行情感分析
    corpus_filepath = "corpus/positive_corpus_v1.txt"
    runout_filepath_ = "runout/dict-positive_test.txt"
    pos_results = ds.analysis_file(corpus_filepath, runout_filepath_, end=pos_test_num)

    corpus_filepath = "corpus/negative_corpus_v1.txt"
    runout_filepath_ = "runout/dict-negative_test.txt"
    neg_results = ds.analysis_file(corpus_filepath, runout_filepath_, end=neg_test_num)

    origin_labels = [1] * pos_test_num + [0] * neg_test_num
    classify_labels = pos_results + neg_results

    filepath = "runout/DictClassifier-pos_train-%d-neg_train-%d-pos_test-%d-neg_test-%d-" \
               "%s.xls" % (pos_train_num, neg_train_num, pos_test_num, neg_test_num,
                           datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    get_accuracy(origin_labels, classify_labels, parameters, filepath)


def test_knn():
    """
    test the classifier based on KNN
    """
    print("KNNClassifier")
    print("---" * 45)

    from classifiers import KNNClassifier
    # k = [1, 3, 5, 7, 9, 11, 13]
    # k = [21, 25, 29, 33, 37, 41, 45]
    k = 45
    knn = KNNClassifier(train_data, train_labels, k=k, best_words=best_words)

    classify_labels = []

    for data in test_data:
        # classify_labels.append(knn.multiple_k_classify(data))
        classify_labels.append(knn.single_k_classify(data))

    # filepath = "runout/KNNClassifier-pos_train-%d-neg_train-%d-pos_test-%d-neg_test-%d-feature-%d-multiple_k-%s" \
    #            "-%s.xls" % (pos_train_num, neg_train_num, pos_test_num, neg_test_num, feature_num,
    #                         "_".join([str(i) for i in k]), datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    filepath = "runout/KNNClassifier-pos_train-%d-neg_train-%d-pos_test-%d-neg_test-%d-feature-%d-k-%s-" \
               "%s.xls" % (pos_train_num, neg_train_num, pos_test_num, neg_test_num, feature_num, str(k),
                           datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    get_accuracy(test_labels, classify_labels, parameters, filepath)


def test_bayes():
    """
    test the classifier based on Naive Bayes
    """
    print("BayesClassifier")
    print("---" * 45)

    from classifiers import BayesClassifier
    bayes = BayesClassifier(train_data, train_labels, best_words)

    classify_labels = []

    for data in test_data:
        classify_labels.append(bayes.classify(data))

    filepath = "runout/BayesClassifier-pos_train-%d-neg_train-%d-pos_test-%d-neg_test-%d-" \
               "feature-%d-%s.xls" % (pos_train_num, neg_train_num, pos_test_num, neg_test_num,
                                      feature_num, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    get_accuracy(test_labels, classify_labels, parameters, filepath)


def test_maxent():
    """
    test the classifier based on Maximum Entropy
    """
    print("MaxEntClassifier")
    print("---" * 45)

    from classifiers import MaxEntClassifier
    max_iter = 800
    maxent = MaxEntClassifier(train_data, train_labels, best_words, max_iter)

    classify_labels = []

    for data in test_data:
        classify_labels.append(maxent.classify(data))

    filepath = "runout/MaxEntClassifier-pos_train-%d-neg_train-%d-pos_test-%d-neg_test-%d-feature-%d-iter-" \
               "%d-%s.xls" % (pos_train_num, neg_train_num, pos_test_num, neg_test_num,
                              feature_num, max_iter, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    get_accuracy(test_labels, classify_labels, parameters, filepath)


def test_svm():
    """
    test the classifier based on Support Vector Machine
    """
    print("SVMClassifier")
    print("---" * 45)

    from classifiers import SVMClassifier
    svm = SVMClassifier(train_data, train_labels)

    classify_labels = []

    for data in test_data:
        classify_labels.append(svm.classify(data))

    filepath = "runout/SVMClassifier-pos_train-%d-neg_train-%d-pos_test-%d-neg_test-%d-tdidf" \
               "-%s.xls" % (pos_train_num, neg_train_num, pos_test_num, neg_test_num,
                            datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    get_accuracy(test_labels, classify_labels, parameters, filepath)


def test_multiple_classifiers():
    """
    test the Fusion of Multiple Classifiers
    """
    print("Fusion of Multiple Classifiers")
    print("---" * 45)

    from classifiers import MultipleClassifiers

    # get the instance of classifiers
    max_iter = 800
    # prob = False
    prob = True

    mc = MultipleClassifiers(train_data, train_labels, best_words, max_iter)

    classify_labels = []
    for data in test_data:
        classify_labels.append(mc.classify(data, prob))

    filepath = "runout/MultipleClassifiers-pos_train-%d-neg_train-%d-pos_test-%d-neg_test-%d-k-1-iter-%d-prob-%s" \
               "-%s.xls" % (pos_train_num, neg_train_num, pos_test_num, neg_test_num,
                            max_iter, "True" if prob else "False",
                            datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    get_accuracy(test_labels, classify_labels, parameters, filepath)


if __name__ == "__main__":
    pos_train_num = neg_train_num = 3500
    pos_test_num = neg_test_num = 1000
    feature_num = 4000
    parameters = [pos_train_num, neg_train_num, pos_test_num, neg_test_num, feature_num]

    # get the corpus
    from waimai import WaimaiCorpus

    corpus = WaimaiCorpus()
    train_data, train_labels = corpus.get_train_corpus(pos_train_num, neg_train_num)
    test_data, test_labels = corpus.get_test_corpus(pos_test_num, neg_test_num)

    # feature extraction
    from feature_extraction import ChiSquare

    fe = ChiSquare(train_data, train_labels)
    best_words = fe.best_words(feature_num)

    # test dict
    # test_dict()

    # test knn
    test_knn()

    # test bayes
    # test_bayes()

    # test maxent
    # test_maxent()

    # test SVM
    # test_svm()

    # test multiple_classifiers
    # test_multiple_classifiers()



