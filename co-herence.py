import argparse
import sys
import operator
import math
import os.path
import cPickle
import codecs
import math

class Coherence(object):
    def __init__(self, metric="npmi", pickle_output=None, topn=10, colloc_sep = "_"):
        self.window_total = 0   #total number of windows
        self.wordcount = {} #a dictionary of word counts, for single and pair words
        self.metric = metric
        self.pickle_output = pickle_output
        self.topn = topn
        self.colloc_sep = "_" #symbol for concatenating collocations

    def _calc_assoc(self, word1, word2):
        combined1 = word1 + "|" + word2
        combined2 = word2 + "|" + word1
    
        combined_count = 0
        if combined1 in self.wordcount:
            combined_count = self.wordcount[combined1]
        elif combined2 in self.wordcount:
            combined_count = self.wordcount[combined2]
        w1_count = 0
        if word1 in self.wordcount:
            w1_count = self.wordcount[word1]
        w2_count = 0
        if word2 in self.wordcount:
            w2_count = self.wordcount[word2]
    
        if (self.metric == "pmi") or (self.metric == "npmi"):
            if w1_count == 0 or w2_count == 0 or combined_count == 0:
                result = 0.0
            else:
                result = math.log((float(combined_count)*float(self.window_total))/ \
                    float(w1_count*w2_count), 10)
                #result = math.log(   (float(combined_count)/self.window_total) / (float(w1_count)/self.window_total) / (float(math.pow(w2_count, 0.75)) / math.pow(self.window_total, 0.75)), 10 )
                if self.metric == "npmi":
                    result = result / (-1.0*math.log(float(combined_count)/(self.window_total),10))
    
                #ppmi
                #if result < 0.0:
                #    result = 0.0
    
        elif self.metric == "lcp":
            if combined_count == 0:
                if w2_count != 0:
                    result = math.log(float(w2_count)/self.window_total, 10)
                else:
                    result = math.log(float(1.0)/self.window_total, 10)
            else:
                result = math.log((float(combined_count))/(float(w1_count)), 10)
    
        return result


    def calc_topic_coherence(self, topic_words):
        topic_assoc = []
        for w1_id in range(0, len(topic_words)-1):
            target_word = topic_words[w1_id]
            #remove the underscore and sub it with space if it's a collocation/bigram
            w1 = " ".join(target_word.split(self.colloc_sep))
            for w2_id in range(w1_id+1, len(topic_words)):
                topic_word = topic_words[w2_id]
                #remove the underscore and sub it with space if it's a collocation/bigram
                w2 = " ".join(topic_word.split(self.colloc_sep))
                if target_word != topic_word:
                    topic_assoc.append(calc_assoc(w1, w2))
    
        return float(sum(topic_assoc))/len(topic_assoc)

    def calc_topics_coherence(self, topic_file, wordcount_file):
        topic_coherence = {} #coherence for each topic; value = ( [num_intruder], [precision] )
        #input
        topic_file = codecs.open(topic_file, "r", "utf-8")
        wc_file = codecs.open(wordcount_file, "r", "utf-8")
        #process the word count file(s)
        for line in wc_file:
            line = line.strip()
            data = line.split("|")
            if len(data) == 2:
                self.wordcount[data[0]] = int(data[1])
            elif len(data) == 3:
                if data[0] < data[1]:
                    key = data[0] + "|" + data[1]
                else:
                    key = data[1] + "|" + data[0]
                self.wordcount[key] = int(data[2])
            else:
                print "ERROR: self.wordcount format incorrect. Line =", line
                raise SystemExit
        
        
        #get the total number of windows
        if WTOTALKEY in self.wordcount:
            self.window_total = self.wordcount[WTOTALKEY]
        
        #open pickle if it exists
        if self.pickle_output != None and os.path.isfile(self.pickle_output):
            topic_coherence = cPickle.load(open(self.pickle_output))
        
        #read the topic file and compute the observed coherence
        topic_tw = {} #{topicid: topN_topicwords}
        topic_id = 0
        for line in topic_file.readlines():
            topic_list = line.split()[:self.topn]
            tw = " ".join(topic_list)
            c = calc_topic_coherence(topic_list)
        
            if debug:
                print ("[%.2f]" % c), tw 
            else:
                print c
        
            if topic_id not in topic_coherence:
                topic_coherence[topic_id] = ([], [])
            topic_coherence[topic_id][0].append(len(topic_list))
            topic_coherence[topic_id][1].append(c)
        
            topic_id += 1