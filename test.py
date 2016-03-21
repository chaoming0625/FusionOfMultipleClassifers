
def test_dict():
    # test the classifier based on Sentiment Dict
    from classifiers import DictClassifier
    ds = DictClassifier()

    # 对一个单句进行情感分析
    # a_sentence = "剁椒鸡蛋好咸,土豆丝很好吃"
    # ds.sentiment_analyse_a_sentence(a_sentence)

    # 对一个文件内语料进行情感分析
    # corpus_filepath = "corpus/positive_corpus_v1.txt"
    # runout_filepath_ = "runout/dict-positive_test.txt"

    corpus_filepath = "corpus/negative_corpus_v1.txt"
    runout_filepath_ = "runout/dict-negative_test.txt"

    r = ds.analysis_file(corpus_filepath, runout_filepath_, end=2000)
    print("Accuracy : %f" % (sum(r) / 2000))


if __name__ == "__main__":
    test_dict()


