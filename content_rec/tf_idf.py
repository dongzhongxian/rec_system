#!/usr/bin/Python
# -*- coding: utf-8 -*-
import os
import pickle
import numpy as np
import jieba
import jieba.posseg as pseg
from math import log
from operator import itemgetter


class IDF(object):
    idf_dir = './data/idf.dict'

    @classmethod
    def _process(cls, corpus_dir):
        """
        All the steps
        :param corpus_dir:
        :return:
        """
        cls.num = 0  # the article number
        cls.article = {}  # stores the collection of all participles under the article
        cls.idf = {}  # idf
        cls.word_set = set()
        cls._calculate_idf(corpus_dir)
        cls.save()

    @classmethod
    def _calculate_idf(cls, corpus_dir):
        """
        calculate idf
        :param corpus_dir:
        :return:
        """
        content = open(corpus_dir, 'rb').read().decode('utf-8')
        for line in content.splitlines():
            cls.num += 1
            words = set(jieba.cut(line))
            cls.article[cls.num] = words
            cls.word_set = cls.word_set | words
        for word in cls.word_set:
            n = 1.0
            for value in cls.article.values():
                if word in value:
                    n += 1.0
            cls.idf[word] = log(cls.num / n)

    @classmethod
    def save(cls):
        """
        save idf model
        :return:
        """
        with open(cls.idf_dir, 'wb') as f:
            pickle.dump(cls.idf, f)

    @classmethod
    def load(cls, corpus_dir):
        """
        load idf model
        :param corpus_dir: Address of corpus to be learned
        :return:
        """
        if not os.path.exists('./data/'):
            os.mkdir('./data/')
        if not os.path.exists(cls.idf_dir):
            cls._process(corpus_dir)
        f = open(cls.idf_dir, 'rb')
        idf = pickle.load(f)
        f.close()
        return idf


class TF_IDF(object):
    """
    Tf_idf algorithm implementation
    need stop words and corpus
    corpus every behavior of an article.
    """

    # allow Part-of-Speech（POS） tagging
    allow_speech_tags = ['an', 'i', 'j', 'l', 'n', 'nr', 'nrfg', 'ns', 'nt',
                         'nz', 't', 'v', 'vd', 'vn', 'eng']

    def __init__(self, corpus_dir):
        self.stop_words = set()
        self._pro_stop_words()
        self.idf = IDF.load(corpus_dir)
        self.new_idf = np.mean(list(self.idf.values()))  # For new words, we use the mean

    def _pro_stop_words(self):
        """
        add stop words
        :return:
        """
        stop_dir = os.path.join('./data/stop_words')
        content = open(stop_dir, 'rb').read().decode('utf-8')
        for line in content.splitlines():
            self.stop_words.add(line)

    def get_tf_idf(self, data, top_k):
        """
        Calculate tf_idf and get topk keyword
        :param data:
        :param top_k:
        :return:
        """
        words = pseg.cut(data)
        # Filter out unexpected POS
        words_filter = [w for w in words if w.flag in self.allow_speech_tags]
        tf = {}
        tf_idf = {}
        word_num = 0
        # Filter stop words and calculate tf
        for w, flag in words_filter:
            if len(w.strip()) < 2 or w.lower() in self.stop_words:
                continue
            word_num += 1
            tf[w] = tf.get(w, 0.0) + 1.0
        # calculate tf-idf
        for key in tf.keys():
            idf = self.new_idf
            if key in self.idf.keys():
                idf = self.idf[key]
            tf_idf[key] = tf_idf.get(key, 0.0) + tf[key] * idf
        tags = sorted(tf_idf.items(), key=itemgetter(1), reverse=True)
        return tags[:top_k]


if __name__ == '__main__':
    corpus_dir = './data/corpus_xueqiu.txt'  # Corpus, each line represents an article
    idf_test = './data/idf_test.txt'  # test article, one line
    text = open(idf_test, 'rb').read().decode('utf-8')
    a = TF_IDF(corpus_dir)
    print(a.get_tf_idf(text, 10))
