# -*- encoding=utf-8 -*-
from bs4 import BeautifulSoup
import xml.dom.minidom
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--s', type=str, help='standard xml', default='../data/test.xml')
parser.add_argument('--t', type=str, help='xml to be tested', default='../predict/predict_result.xml')
parser.add_argument('--r', type=str, help='xml to store the result', default='test_result_fuzzy.xml')
args = parser.parse_args()

def getEmployee(tag):
    employee_set = set()
    for i, t in enumerate(tag.contents):
        if(i == 0): continue
        employee_set.add((t['name'],t['from']))
    return employee_set

# xml_standard = '../data/test.xml'
# xml_test = 'beTested.xml'
# xml_result = 'predict_result.xml'
xml_standard = args.s
xml_test = args.t
xml_result = args.r

doc_result = xml.dom.minidom.Document()
root_result = doc_result.createElement('weibos')
doc_result.appendChild(root_result)

soup_standard = BeautifulSoup(open(xml_standard, 'r'), features='lxml')
soup_test = BeautifulSoup(open(xml_test, 'r'), features='lxml')

content_standard = soup_standard.weibos.contents
content_test = soup_test.weibos.contents

assert len(content_standard) == len(content_test), 'the lengths of standard xml and test xml are not same'

FP = 0
FN = 0

answer = 0
predict = 0
correct = 0


for i, (tag_standard, tag_test) in enumerate(zip(content_standard, content_test)):
    text_standard = tag_standard.contents[0]
    text_test = tag_test.contents[0]
    if(not text_standard == text_test):
        print "texts in standard xml and test xml can't match!"
        print text_standard
        print text_test
    node_weibo = doc_result.createElement('weibo')
    node_weibo.appendChild(doc_result.createTextNode(text_standard.encode('utf8')))
    node_weibo.setAttribute('id', str(i + 1))
    employee_set_standard = getEmployee(tag_standard)
    employee_set_test = getEmployee(tag_test)

    answer += len(employee_set_standard)
    predict += len(employee_set_test)

    set_standard_match = set()
    set_test_match = set()
    set_match = dict()

    for test in employee_set_test:
        for standard in employee_set_standard:
            if(test[0] == standard[0] and test[1] == standard[1]):
                set_standard_match.add(standard)
                employee_set_standard.remove(standard)
                set_test_match.add(test)
                if(standard not in set_match.keys()):
                    set_match[standard] = list()
                set_match[standard].append(test)
                break

    correct += len(set_standard_match)

    set_FP = employee_set_test - set_test_match
    set_FN = employee_set_standard - set_standard_match

    FP += len(set_FP)
    FN += len(set_FN)

    for standard, test_list in set_match.items():
        node_employee = doc_result.createElement('employee')
        node_employee.setAttribute('from', standard[1].encode('utf8'))
        node_employee.setAttribute('name', standard[0].encode('utf8'))
        node_employee.setAttribute('result', 'TP')

        for test in test_list:
            node_test = doc_result.createElement('match')
            node_test.setAttribute('from', test[1].encode('utf8'))
            node_test.setAttribute('name', test[0].encode('utf8'))

            node_employee.appendChild(node_test)

        node_weibo.appendChild(node_employee)

    for relation in set_FN:
        node_employee = doc_result.createElement('employee')
        node_employee.setAttribute('from', relation[1].encode('utf8'))
        node_employee.setAttribute('name', relation[0].encode('utf8'))
        node_employee.setAttribute('result', 'FN')

        node_weibo.appendChild(node_employee)

    for relation in set_FP:
        node_employee = doc_result.createElement('employee')
        node_employee.setAttribute('from', relation[1].encode('utf8'))
        node_employee.setAttribute('name', relation[0].encode('utf8'))
        node_employee.setAttribute('result', 'FP')

        node_weibo.appendChild(node_employee)

    root_result.appendChild(node_weibo)

print 'answer = ', answer
print 'predict = ', predict
print 'correct = ', correct

print 'FP = ', FP
print 'FN = ', FN

print 'Precison = ', float(correct) / predict
print 'Recall = ', float(correct) / answer

print 'F1 score = ', 2 / (predict / float(correct) + answer / float(correct))

with open(xml_result, 'w') as f:
    doc_result.writexml(f, encoding='utf8')
