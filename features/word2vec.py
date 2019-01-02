# -*- encoding=utf-8 -*-
import pickle
import os

class Word2Vector(object):
    def __init__(self):
        self.words = list()
        self.positions = list()
        self.word_nums = 0

        self.load('../word_list/merge_sgns_bigram_char300.txt', '../word_list/words_list.pkl')

    def load(self, model_path, words_path):
        print 'loading words vectors ...'
        self.model_path = model_path
        self.words_path = words_path

        if(not os.path.isfile(words_path)):
            self.generate_words_list(self.model_path, self.words_path)
        with open(self.words_path, 'r') as f:
            self.words, self.positions = pickle.load(f)
        self.word_nums = len(self.words)
        print 'total words : {0}'.format(self.word_nums)
    def generate_words_list(self, model_path, words_path):
        i = 0
        words = list()
        positions = list()
        with open(model_path, 'r') as f:
            while True:
                pos = f.tell()
                line = f.readline()
                i += 1
                if(not line):
                    break
                if(i == 1):
                    self.word_nums = int(line.split()[0])
                    words = [None] * self.word_nums
                    positions = [0] * self.word_nums
                else:
                    positions[i - 2] = pos
                    word, vector = line.split(' ', 1)
                    words[i - 2] = word

                if(i % 100000 == 0):
                    print '{0}%'.format(i * 100 // self.word_nums)
        with open(words_path, 'w') as f:
            pickle.dump((words,positions), f)
    def vector(self, word):
        if word not in self.words:
            return None
        index = self.words.index(word)
        with open(self.model_path, 'r') as f:
            f.seek(self.positions[index])
            line = f.readline()
            assert line.split(' ', 1)[0] == word, 'word can not match'

            vec = line.split(' ', 1)[1]
            vec = [float(x) for x in vec.split()]

            assert len(vec) == 300, 'vector length is not 300'

            return vec
