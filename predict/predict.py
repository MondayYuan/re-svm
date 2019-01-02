# -*- encoding=utf-8 -*-
import sys

sys.path.append('../data')
from xml_util import loader
from xml_util import saver
sys.path.append('../features')
from ltp import TextProcessor
from word2vec import Word2Vector

from feature_extraction import TextFeatures

from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser

from svmutil import *

class AllTextsPredictor(object):
    def __init__(self, input_xml, output_xml, svm_model='../train/svm.model'):
        self.input_xml = input_xml
        self.output_xml = output_xml

        self.contents = loader(input_xml)

        self.svm_model = svm_load_model(svm_model)

        self.contents_predict = list()

        self.word2vector = Word2Vector()

        self.text_processor = TextProcessor()


    def predict(self):
        for i, (text, _) in enumerate(self.contents):
            print '{0}/{1}'.format(i, len(self.contents))
            text_predictor = TextPredictor(text, self.svm_model, self.text_processor, self.word2vector)
            text_predictor.predict()
            self.contents_predict.append((text, text_predictor.relations_predict))
        self.save_result()


    def save_result(self):
        saver(self.contents_predict, self.output_xml)

class TextPredictor(object):
    def __init__(self, text, svm_model, text_processor, word2vector):
        self.text = text
        self.svm_model = svm_model
        self.text_processor = text_processor
        self.word2vector = word2vector

        self.relations_predict = list()
        self.features = list()

        self.x = list()

    def generate_features(self):
        text_features = TextFeatures(self.text, self.text_processor, self.word2vector)
        text_features.extract()
        self.features = text_features.unknown_features
        self.relations = text_features.unknown_relations

        _, self.x = self.svm_read_problem_list(self.features)

    def svm_read_problem_list(self, features_list):
        prob_y = []
        prob_x = []
        for i, line in enumerate(features_list):
            line = line.split(None, 1)
            # In case an instance with all zero features
            if len(line) == 1: line += ['']
            label, features = line
            prob_y += [float(label)]

            xi = {}
            for e in features.split():
                ind, val = e.split(":")
                xi[int(ind)] = float(val)
            prob_x += [xi]

        return (prob_y, prob_x)

    def predict(self):
        self.generate_features()
        if(self.x):
            self.p_labels = svm_predict([], self.x, self.svm_model)[0]
        else:
            self.p_labels = list()

        for i, label in enumerate(self.p_labels):
            if(label == 1):
                self.relations_predict.append(self.relations[i])
        #去掉同意词
        self.relations_predict = self.merge_relation_list(self.relations_predict)

    def merge_relation_list(self, relation_list):
        new_list = list()
        for relation in relation_list:
            match_relation = self.fuzzy_match(new_list, relation)
            if(match_relation):
                if(relation[1] in match_relation[1]):
                    new_list.remove(match_relation)
                    new_list.append(relation)
            else:
                new_list.append(relation)
        return new_list

    def fuzzy_match(self, relation_list, relation):
        for r in relation_list:
            if(r[0] == relation[0] and (r[1] in relation[1] or relation[1] in r[1])):
                return r
        return None


if __name__ == '__main__':
    AllTextsPredictor('../data/test_no_label.xml', 'predict_result.xml').predict()
