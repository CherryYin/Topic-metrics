import argparse
import sys
import operator
import math
import os.path
import cPickle
import codecs
import numpy as np

class Diversity(object):
    def __init__(self, topn=25, colloc_sep = "_"):
        self.topn = topn #a dictionary of word counts, for single and pair words

    def _calc_unique_num(self, topic_words, other_topic_words):
        uniq_num = 0
        for t_w in topic_words:
            if t_w not in other_topic_words:
                uniq_num += 1
        return uniq_num

    def cal_topic_diversity(self, topics_words):
        uniq_ratios = []
        topic_num = len(topics_words)
        for i in range(topic_num):
            topic_words = topics_words[i]
            other_topic_words = set()
            for j in range(topic_num):
                if i == j:
                    continue
                other_topic_words.update(topics_words[j])
            uniq_num = self._calc_unique_num(topic_words, other_topic_words)
            uniq_ratio = uniq_num / self.topn
            uniq_ratios.append(uniq_ratio)
        uniq_ratios = np.array(uniq_ratios)
        td = uniq_ratios.mean()

        return td
                