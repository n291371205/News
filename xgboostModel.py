import numpy as np
import os
import codecs
import scipy.io as scio
import random
from scipy.spatial.distance import pdist
# from metric_learn import NCA, Covariance, LMNN, MLKR, ITML_Supervised, RCA_Supervised, LSML_Supervised, MMC_Supervised, LFDA
import tensorflow as tf
import matplotlib.pyplot as plt
import time
from sklearn.decomposition import PCA
import xgboost as xgb
import sklearn.model_selection as sk
from scipy import sparse
import pickle 
import sys
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
 
# 计算分类正确率
from sklearn.metrics import accuracy_score
PATH_CURR = os.path.abspath(".")

def getData_old():
    PATH_DATA = PATH_CURR + '/feature_transformation/'
    
    data = scio.loadmat(PATH_DATA + 'newData.mat')
    # print(data['x'].shape)
    # print(data['y'])
#     print(ca)
    
    #得到训练集和测试集
    m = random.sample(range(0, data["x"].shape[0]), 2400)
    train_data_X = []
    train_data_Y = []
    test_data_X = []
    test_data_Y = []
    
    flag_first1 = True
    flag_first2 = True
    
    for i in range(0,len(m)-400):
        if flag_first1:
            flag_first1 = False
            train_data_X =  sparse.coo_matrix.getrow(data['x'],m[i])
        else:
            train_data_X = sparse.vstack([train_data_X,sparse.coo_matrix.getrow(data['x'],m[i])])
        train_data_Y.append(data["y"][0][m[i]])

    for i in range(len(m)-400,len(m)):
        if flag_first2:
            flag_first2 = False
            test_data_X =  sparse.coo_matrix.getrow(data['x'],m[i])
        else:
            test_data_X = sparse.vstack([test_data_X,sparse.coo_matrix.getrow(data['x'],m[i])])
        test_data_Y.append(data["y"][0][m[i]])
    
    # print(test_data_Y)
    train_data_Y = np.expand_dims(train_data_Y, axis=1)
    test_data_Y = np.expand_dims(test_data_Y, axis=1)
    
    return train_data_X,train_data_Y,test_data_X,test_data_Y


def runModel(modelName, num):

    train_data_X,train_data_Y,test_data_X,test_data_Y = getData_old()

    dtrain = xgb.DMatrix(train_data_X, train_data_Y)
    dtest = xgb.DMatrix(test_data_X, test_data_Y)

    # print(dtrain.get_label())
    # print(ca)



    # specify parameters via map
    # params = {'max_depth':10, 'eta':1, 'silent':1, 'objective':'binary:logistic' }

    watchlist = [ (dtrain,'train'), (dtest, 'test') ]  

    params={
        'booster':'gbtree',
        'objective': 'binary:logistic', 
        'gamma':0.8,  # 在树的叶子节点下一个分区的最小损失，越大算法模型越保守 。[0:]
        'max_depth':6, # 构建树的深度 [1:]
        'lambda':100,  # L2 正则项权重
        'subsample':0.5, # 采样训练数据，设置为0.5，随机选择一般的数据实例 (0:1]
        'colsample_bytree':1, # 构建树树时的采样比率 (0:1]
        'min_child_weight':12, # 节点的最少特征数
        'silent':1 ,
        'eta': 0.1, # 如同学习率
        'seed':30,
        'nthread':4,# cpu 线程数,根据自己U的个数适当调整
    }

    # 设置boosting迭代计算次数
    num_round = num

    bst = xgb.train(params, dtrain, num_round, watchlist)  # dtrain是训练数据集


    train_preds = bst.predict(dtrain)    #
    # print ("train_preds",train_preds)
    
    train_predictions = [round(value) for value in train_preds]
    # print ("train_predictions",train_predictions)
    
    y_train = dtrain.get_label()
    # print ("y_train",y_train)
    
    train_accuracy = accuracy_score(y_train, train_predictions)
    # log.info ("Train Accuary: %.2f%%" % (train_accuracy * 100.0))
    

    # make prediction
    preds = bst.predict(dtest)
    predictions = [round(value) for value in preds]
    # log.info ("preds："+str(preds)) 
    # log.info ("predictions："+str(predictions))

    y_test = dtest.get_label()
    # log.info ("y_test："+str(y_test))
    
    test_accuracy = accuracy_score(y_test, predictions)
    # log.info("Test Accuracy: "+str(test_accuracy * 100.0)+"%")

    #save model
    with open(PATH_CURR + '/modelSave/' + modelName + '.pik','wb')as f:  
        pickle.dump(bst,f,-1)

    