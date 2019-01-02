# -*- encoding=utf-8 -*-
from svmutil import *
import sys
sys.path.append('../libsvm/tools')
from grid import find_parameters

features_train = '../features/features_train.txt'
features_test = '../features/features_test.txt'

y, x = svm_read_problem(features_train)

#调用./libsvm/tools/grid.py 暴力调参
# params = svm_parameter(find_parameters(features_test))

params = svm_parameter('-c 32.0 -g 0.0078125')

m = svm_train(svm_problem(y, x), params)
svm_save_model('svm.model', m)

print 'accuracy of svm in train set:'
svm_predict(y, x, m)
print 'accuracy of svm in test set:'
yt, xt = svm_read_problem(features_test)
p_labels, p_acc, p_val = svm_predict(yt, xt, m)
