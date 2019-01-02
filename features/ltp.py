# -*- encoding=utf-8 -*-

from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser

class TextProcessor(object):
    def __init__(self):
        self.segmentor = Segmentor()
        self.postagger = Postagger()
        self.recognizer = NamedEntityRecognizer()
        self.parser = Parser()
        # self.segmentor.load("ltp_data/cws.model")
        # self.postagger.load("ltp_data/pos.model")
        self.segmentor.load_with_lexicon("../ltp_data/cws.model", '../data/segmentor_lexicon.txt')
        self.postagger.load_with_lexicon("../ltp_data/pos.model", '../data/postagger_lexicon.txt')
        self.recognizer.load("../ltp_data/ner.model")
        self.parser.load('../ltp_data/parser.model')

        self.text = ''
        self.words = list()
        self.postags = list()
        self.netags = list()

    def process(self, text):
        self.text = text
        self.words = self.segmentor.segment(self.text)
        self.postags = self.postagger.postag(self.words)
        self.netags = self.recognizer.recognize(self.words, self.postags)
        self.arcs = self.parser.parse(self.words, self.postags)
