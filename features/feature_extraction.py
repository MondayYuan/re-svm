# -*- encoding=utf-8 -*-
import sys
sys.path.append('../data')
from xml_util import loader
from xml_util import saver
from ltp import TextProcessor
from word2vec import Word2Vector
import random


class AllTextsFeatures(object):
    def __init__(self, input_file, output_file, times=None):
        self.output_file = output_file
        self.times = times #负样本是正样本数量的倍数
        self.contents = loader(input_file)

        self.positive_features = list()
        self.negtive_features = list()
        self.total_features = list()

        self.text_processor = TextProcessor()

        self.word2vector = Word2Vector()

    def extract(self):
        for i, (text, answers) in enumerate(self.contents):
            print '{0}/{1}'.format(i, len(self.contents))
            text_features = TextFeatures(text, self.text_processor, self.word2vector, answers, self.times)
            text_features.extract()
            self.positive_features += text_features.positive_features
            self.negtive_features += text_features.negtive_features
        self.mix_features()


    def mix_features(self):
        if self.times == None:
            self.times = float(len(self.negtive_features)) / len(self.positive_features)
        negative_len = min(int(self.times * len(self.positive_features)), len(self.negtive_features))
        random.shuffle(self.negtive_features)
        self.total_features = self.positive_features + self.negtive_features[0: negative_len]
        random.shuffle(self.total_features)


    def save_features(self):
        with open(self.output_file, 'w') as f:
            for feature in self.total_features:
                f.write(feature + '\n')

    def run(self):
        print 'generate features ...'
        self.extract()
        self.save_features()


class TextFeatures(object):
    def __init__(self, text, text_processor, word2vec, answers=None, times=None):
        self.text = text
        self.text_processor = text_processor
        self.word2vec = word2vec
        self.answers = answers
        self.times = None

        self.positive_features = list()
        self.negtive_features = list()
        self.unknown_features = list()

        self.positive_relations = list()
        self.negtive_relations = list()
        self.unknown_relations = list()

    def extract(self):
        name_entities_person = list()
        name_entities_organization = list()

        self.text_processor.process(self.text)
        netags = self.text_processor.netags
        words = self.text_processor.words

        for i in range(len(netags)):
            if (netags[i] in ['B-Nh', 'S-Nh']):
                name_entities_person.append(words[i])
            elif (netags[i] in ['B-Ni', 'B-Ns', 'S-Ni', 'S-Ns']):
                name_entities_organization.append(words[i])
            elif (netags[i] in ['I-Nh', 'E-Nh']):
                name_entities_person[-1] += words[i]
            elif (netags[i] in ['I-Ni', 'E-Ni', 'I-Ns', 'E-Ns']):
                name_entities_organization[-1] += words[i]

        if(self.answers):
            for relation in self.answers:
                self.positive_relations.append(relation)


            for person in name_entities_person:
                for orgazation in name_entities_organization:
                    # 之前已经加入正样本中了
                    if ((person, orgazation) in self.answers):
                        continue
                    if (self.fuzzy_match_list(person, orgazation, self.answers)):
                        self.positive_relations.append((person, orgazation))
                    else:
                        self.negtive_relations.append((person, orgazation))
            # 去重
            self.positive_relations = list(set(self.positive_relations))
            self.negtive_relations = list(set(self.negtive_relations))

            if (self.times):
                random.shuffle(self.negtive_relations)
                negative_len = min(int(self.times * len(self.positive_relations)), len(self.negtive_relations))
                self.negtive_relations = self.negtive_relations[0:negative_len]

        else:
            for person in name_entities_person:
                for orgazation in name_entities_organization:
                    self.unknown_relations.append((person, orgazation))
            self.unknown_relations = list(set(self.unknown_relations))


        self.generate_features_for_one_text()

    def generate_features_for_one_text(self):
        for person, organization in self.positive_relations:
            feature = RelationFeature(self.text, person, organization, 1, self.text_processor, self.word2vec).extract()
            if(feature):
                self.positive_features.append(feature)
        for person, organization in self.negtive_relations:
            feature = RelationFeature(self.text, person, organization, -1, self.text_processor, self.word2vec).extract()
            if(feature):
                self.negtive_features.append(feature)
        for person, organization in self.unknown_relations:
            feature = RelationFeature(self.text, person, organization, 0, self.text_processor, self.word2vec).extract()
            if(feature):
                self.unknown_features.append(feature)
            else:
                self.unknown_relations.remove((person, organization))

    @staticmethod
    def fuzzy_match(per1, org1, per2, org2):
        if (per1 == per2 and (org1 in org2 or org2 in org1)):
            return True
        else:
            return False

    def fuzzy_match_list(self, per, org, relation_list):
        flag = False
        for relation in relation_list:
            if (self.fuzzy_match(per, org, relation[0], relation[1])):
                flag = True
                break
        return flag


class RelationFeature(object):
    def __init__(self, text, person, organization, label, text_processor, word2vec, max_dis=None):

        self.max_dis = max_dis

        self.label = label
        self.person = person
        self.organization = organization
        self.text = text

        self.feature = str(self.label)
        self.feature_end_index = 0

        self.words = text_processor.words
        self.postags = text_processor.postags
        self.netags = text_processor.netags
        self.arcs = text_processor.arcs

        self.postage_table = ['a', 'b', 'c', 'd', 'e', 'g', 'h', 'i', 'j', 'k', 'm', 'n', 'nd',
                              'nh', 'ni', 'nl', 'ns', 'nt', 'nz', 'o', 'p', 'q', 'r', 'u', 'v',
                              'wp', 'ws', 'x', 'z']

        self.arc_table = ['SBV', 'VOB', 'IOB', 'FOB', 'DBL', 'ATT', 'ADV', 'CMP', 'COO', 'POB',
                          'LAD', 'RAD', 'IS', 'HED']

        self.word2vec = word2vec



    def extract(self):
        self.get_position(self.person, self.organization)

        dis = min(abs(self.person_pos[0] - self.organization_pos[1]), abs(self.organization_pos[0] - self.person_pos[1]))
        if(self.max_dis and dis > self.max_dis):
            return None
        if (self.person_pos == (-1, -1) and self.organization_pos == (-1, -1)):
            return None

        # 位置特征
        self.feature += ' 1:{0} 2:{1} 3:{2} 4:{3}' \
            .format(self.person_pos[1] - self.person_pos[0] + 1,
                    self.organization_pos[1] - self.organization_pos[0] + 1,
                    self.organization_pos[1] - self.person_pos[0],
                    self.person_pos[0] - self.organization_pos[1]
                    )
        self.feature_end_index += 4
        #词向量特征
        self.add_word_vector_feature(self.person)
        self.add_word_vector_feature(self.organization)
        #判断两个实体间有没有其他实体
        entities_num_between_relation = self.get_entities_num_between_relation(self.person_pos, self.organization_pos, self.netags)
        # if(self.label > 0):
        #     print entities_num_between_relation
        self.feature += ' {0}:{1}'.format(self.feature_end_index + 1, entities_num_between_relation)
        self.feature_end_index += 1
        # 词性特征, 用one hot表示
        self.add_postag_feature_for_one_word(self.person_pos[0])
        self.add_postag_feature_for_one_word(self.organization_pos[0])
        # 相邻词性特征
        self.add_neighbor_postag(self.person_pos[0], self.person_pos[1], 3)
        self.add_neighbor_postag(self.organization_pos[0], self.organization_pos[1], 3)
        # 句法特征
        #self.add_arc_feature_for_word(self.person_pos[1], 1, 1)
        #self.add_arc_feature_for_word(self.organization_pos[1], 1, 1)
        self.add_arc_feature(self.arcs, self.person_pos, self.organization_pos)

        return self.feature

    def add_word_vector_feature(self, entity):
        vec = self.word2vec.vector(entity)
        if(not vec):
            self.feature_end_index += 300
        else:
            for i in range(300):
                self.feature += ' {0}:{1}'.format(self.feature_end_index + i + 1, vec[i])
            self.feature_end_index += 300

    def get_entities_num_between_relation(self, per_pos, org_pos, netag_list):

        left = min(per_pos[1], org_pos[1])
        right = max(per_pos[0], org_pos[0])

        if(left < 0 or right < 0):
            return 0

        count = 0

        for i in range(left + 1, right):
            if(netag_list[i][0] == 'S' or netag_list[i][0] == 'B'):
                count += 1
        return count

    def get_position(self, person, organization):
        word = str()
        person_positions = list()
        organization_positions = list()
        word_list = list()
        for i in range(len(self.words)):
            if (self.netags[i][0] == 'B'):
                word = self.words[i]
                start = i
            elif (self.netags[i][0] == 'I'):
                word += self.words[i]
            elif (self.netags[i][0] == 'E'):
                word += self.words[i]
                end = i
                word_list.append(word)
                if (word == person):
                    person_positions.append((start, end))
                elif (word in organization or organization in word):
                    organization_positions.append((start, end))
            elif (self.netags[i][0] == 'S'):
                start = end = i
                word = self.words[i]
                word_list.append(word)
                if (word == person):
                    person_positions.append((start, end))
                elif (word in organization or organization in word):
                    organization_positions.append((start, end))

        # 选择两个最近的位置
        min_dis = 999999999999999999
        person_pos = (-1, -1)
        organization_pos = (-1, -1)
        for per_pos in person_positions:
            for org_pos in organization_positions:
                dis = max(0, max(per_pos[0], org_pos[0]) - min(per_pos[1], org_pos[1]))
                if dis < min_dis:
                    min_dis = dis
                    person_pos = per_pos
                    organization_pos = org_pos

        self.person_pos, self.organization_pos = person_pos, organization_pos

    def add_arc_feature(self, arcs, per_pos, org_pos):
        flag = False
        for i in range(per_pos[0], per_pos[1] + 1):
            head = arcs[i].head
            if(arcs[i].relation == 'ATT' and head - 1 >= org_pos[0] and head - 1 <= org_pos[1]):
                flag = True
                break

            elif(head > 0 and arcs[head - 1].relation == 'ATT' and arcs[head - 1].head - 1 >= org_pos[0] and arcs[head - 1].head - 1 <= org_pos[1]):
                flag = True
                break
        if(flag):
            self.feature += ' {0}:1'.format(self.feature_end_index + 1)
        self.feature_end_index += 1
            # arc_relation_index = self.feature_end_index + 1 + self.arc_table.index(relation)
            # self.feature += ' {0}:1'.format(arc_relation_index)
            # self.feature_end_index += len(self.arc_table)
        # else:
        #     # self.feature_end_index += 1 + len(self.arc_table)



    def add_neighbor_postag(self, start, end, k_neighors):
        if(start < 0 or end < 0):
            self.feature_end_index += 2 * k_neighors * len(self.postage_table)
            return
        for i in range(start - k_neighors, start):
            self.add_postag_feature_for_one_word(i)
        for i in range(end + 1 ,end + k_neighors + 1):
            self.add_postag_feature_for_one_word(i)

    def add_postag_feature_for_one_word(self, Index):
        if(Index >= 0 and Index < len(self.postags)):
            postag_index = self.postage_table.index(self.postags[Index]) + self.feature_end_index + 1
            self.feature += ' {0}:1'.format(postag_index)
        self.feature_end_index += len(self.postage_table)


if __name__ == '__main__':
    AllTextsFeatures('../data/train.xml', 'features_train.txt', 4).run()
    AllTextsFeatures('../data/test.xml', 'features_test.txt', 4).run()

