from fomc.tools import get_accuracy
import datetime


def test_knn():
    """
    test the classifier based on KNN
    """
    print("KNNClassifier")
    print("---" * 45)

    from fomc.classifiers import KNNClassifier
    # k = [1, 3, 5, 7, 9, 11, 13]
    # k = [21, 25, 29, 33, 37, 41, 45]
    k = 1
    knn = KNNClassifier(train_data, train_labels, k=k, best_words=best_words)

    classify_labels = []

    print("KNNClassifiers is testing ...")
    for data in test_data:
        classify_labels.append(knn.classify(data))
    print("KNNClassifiers tests over.")

    filepath = "f_runout/KNN2-movie-pt-%d-%d-nt-%d-%d-f-%d-k-%d-%s.xls" % (
        pos_train_num, pos_test_num, neg_train_num, neg_test_num, feature_num, k,
        datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    get_accuracy(test_labels, classify_labels, parameters, filepath)


def test_bayes():
    """
    test the classifier based on Naive Bayes
    """
    print("BayesClassifier")
    print("---" * 45)

    from fomc.classifiers import BayesClassifier
    bayes = BayesClassifier(train_data, train_labels, best_words)

    classify_labels = []
    print("BayesClassifier is testing ...")
    for data in test_data:
        classify_labels.append(bayes.classify(data))
    print("BayesClassifier tests over.")

    filepath = "f_runout/Bayes-movie-pt-%d-%d-nt-%d-%d-f-%d-%s.xls" % (
        pos_train_num, pos_test_num, neg_train_num, neg_test_num, feature_num,
        datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    get_accuracy(test_labels, classify_labels, parameters, filepath)


def test_maxent_iteration():
    """
    test the classifier based on Maximum Entropy
    """
    print("MaxEntClassifier")
    print("---" * 45)

    from fomc.classifiers import MaxEntClassifier
    maxent = MaxEntClassifier(train_data, train_labels, best_words, max_iter,
                              test=True, test_data=test_data, test_labels=test_labels, what="movie")


def test_maxent():
    """
    test the classifier based on Maximum Entropy
    """
    print("MaxEntClassifier")
    print("---" * 45)

    from fomc.classifiers import MaxEntClassifier
    maxent = MaxEntClassifier(train_data, train_labels, best_words, max_iter)

    classify_labels = []
    print("MaxEntClassifier is testing ...")
    for data in test_data:
        classify_labels.append(maxent.classify(data))
    print("MaxEntClassifier tests over.")

    filepath = "f_runout/MaxEnt-movie-pt-%d-%d-nt-%d-%d-f-%d-iter-%d-%s.xls" % (
        pos_train_num, pos_test_num, neg_train_num, neg_test_num, feature_num, max_iter,
        datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    get_accuracy(test_labels, classify_labels, parameters, filepath)


def test_svm():
    """
    test the classifier based on Support Vector Machine
    """
    print("SVMClassifier")
    print("---" * 45)

    from fomc.classifiers import SVMClassifier
    svm = SVMClassifier(train_data, train_labels, best_words, C)

    classify_labels = []
    print("SVMClassifier is testing ...")
    for data in test_data:
        classify_labels.append(svm.classify(data))
    print("SVMClassifier tests over.")

    filepath = "f_runout/SVM-movie-pt-%d-%d-nt-%d-%d-f-%d-C-%d-%s-lin.xls" % (
        pos_train_num, pos_test_num, neg_train_num, neg_test_num, feature_num, C,
        datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    get_accuracy(test_labels, classify_labels, parameters, filepath)


def test_multiple_classifiers():
    """
    test the Fusion of Multiple Classifiers
    """
    print("Fusion of Multiple Classifiers")
    print("---" * 45)

    from fomc.classifiers import MovieMultipleClassifiers

    # get the instance of classifiers
    # prob = False
    prob = True
    knn = False

    mc = MovieMultipleClassifiers(train_data, train_labels, best_words, max_iter, C, knn)

    print("movieMultipleClassifiers is testing ...")
    classify_labels = []
    for data in test_data:
        classify_labels.append(mc.classify(data, prob))

    print("movieMultipleClassifiers tests over.")

    filepath = "f_runout/Multiple-movie-pt-%d-%d-nt-%d-%d-iter-%d-C-%d-k-%s-prob-%s-%s.xls" % (
        pos_train_num, pos_test_num, neg_train_num, neg_test_num, max_iter, C, "True" if knn else "False",
        "True" if prob else "False", datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    get_accuracy(test_labels, classify_labels, parameters, filepath)


def test_multiple_classifiers2():
    """
    test the Fusion of Multiple Classifiers
    """
    print("Fusion of Multiple Classifiers")
    print("---" * 45)

    from fomc.classifiers import MovieMultipleClassifiers2

    # get the instance of classifiers
    # prob = False

    mc = MovieMultipleClassifiers2(train_data, train_labels, best_words, max_iter, C)

    print("movieMultipleClassifiers is testing ...")
    classify_labels = []
    for data in test_data:
        classify_labels.append(mc.classify(data))

    print("movieMultipleClassifiers tests over.")

    filepath = "f_runout/Multiple2-movie-pt-%d-%d-nt-%d-%d-iter-%d-C-%d-%s.xls" % (
        pos_train_num, pos_test_num, neg_train_num, neg_test_num, max_iter, C,
        datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    get_accuracy(test_labels, classify_labels, parameters, filepath)


def test_multiple_classifiers3():
    """
    test the Fusion of Multiple Classifiers
    """
    print("Fusion of Multiple Classifiers")
    print("---" * 45)

    from fomc.classifiers import MovieMultipleClassifiers3

    mc = MovieMultipleClassifiers3(train_data, train_labels, best_words, max_iter, C)

    print("movieMultipleClassifiers is testing ...")
    classify_labels = []
    for data in test_data:
        classify_labels.append(mc.classify(data))

    print("movieMultipleClassifiers tests over.")

    filepath = "f_runout/Multiple4-movie-pt-%d-%d-nt-%d-%d-iter-%d-C-%d-%s.xls" % (
        pos_train_num, pos_test_num, neg_train_num, neg_test_num, max_iter, C,
        datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    get_accuracy(test_labels, classify_labels, parameters, filepath)


def test_multiple_classifiers4():
    """
    串并联：投票决策
    """
    print("Fusion of Multiple Classifiers")
    print("---" * 45)

    from fomc.classifiers import MovieMultipleClassifiers4

    mc = MovieMultipleClassifiers4(train_data, train_labels, best_words, max_iter, C)

    print("movieMultipleClassifiers is testing ...")
    classify_labels = []
    for data in test_data:
        classify_labels.append(mc.classify(data))

    print("movieMultipleClassifiers tests over.")

    filepath = "f_runout/Multiple5-movie-pt-%d-%d-nt-%d-%d-iter-%d-C-%d-%s.xls" % (
        pos_train_num, pos_test_num, neg_train_num, neg_test_num, max_iter, C,
        datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    get_accuracy(test_labels, classify_labels, parameters, filepath)


if __name__ == "__main__":
    pos_train_num = neg_train_num = 500
    pos_test_num = neg_test_num = 200
    feature_num = 4000
    max_iter = 10
    C = 10
    parameters = [pos_train_num, neg_train_num, pos_test_num, neg_test_num, feature_num]

    # get the f_corpus
    from fomc.corpus import MovieCorpus

    corpus = MovieCorpus()
    train_data, train_labels = corpus.get_train_corpus(pos_train_num, neg_train_num)
    test_data, test_labels = corpus.get_test_corpus(pos_test_num, neg_test_num)

    # feature extraction
    from fomc.feature_extraction import ChiSquare

    fe = ChiSquare(train_data, train_labels)
    best_words = fe.best_words(feature_num)

    # test knn
    # test_knn()

    # test bayes
    # test_bayes()

    # test maxent
    # test_maxent()
    # test_maxent_iteration()

    # test SVM
    # test_svm()

    # test multiple_classifiers
    # test_multiple_classifiers()
    # test_multiple_classifiers2()
    # test_multiple_classifiers3()
    test_multiple_classifiers4()

