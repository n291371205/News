
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
import feature1
import sys
import logging
import model_train_svm
import pickle
import feature2 as fea
# 计算分类正确率
from sklearn.metrics import accuracy_score


def modelGenerate(modelName, ratio, num):

	log = logging.getLogger()
	log.setLevel(logging.DEBUG)
	ch = logging.StreamHandler(sys.stdout)
	ch.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	ch.setFormatter(formatter)
	log.addHandler(ch)

	FILE_NUM = -1
	PATH_CURR = os.path.abspath(".")
	PATH_NEWS = PATH_CURR + "/news/"


	#生成newcontent-------------------------------------------------------------------
	for root, dirs, files in os.walk(PATH_NEWS):  

		count = 0
		# print(files) #当前路径下所有非目录子文件  
		with open(PATH_CURR+"/news_content.txt","w",encoding="utf-8") as f:
			for file in files:
				with open(PATH_NEWS + file,"r",encoding="utf-8") as f1:
					f.write(f1.read())

	#生成label_ind-------------------------------------------------------------------
	def file_name(file_dir):   
		for root, dirs, files in os.walk(file_dir):
			pass
		return files
		

	files = file_name(PATH_NEWS)
	# print(files)
	FILE_NUM = len(files)
	with open(PATH_CURR+"/label_ind.txt","w",encoding="utf-8") as f:
		for i in range(0,len(files)):
			# print(i)
			f.write(files[i][0:len(files[i])-4]+'\t'+str(i))
			f.write('\n')


	#生成dict-------------------------------------------------------------------
	from sklearn.datasets import load_files
	from sklearn.model_selection import train_test_split
	from sklearn.preprocessing import MultiLabelBinarizer
	from sklearn.preprocessing import LabelBinarizer
	from scipy.sparse import coo_matrix, hstack, vstack

	PATH_DATA = PATH_CURR + '\\news_content.txt'

	# 1:BOW  2:DM
	feature_option = 1
	import codecs
	newsdata = codecs.open(PATH_DATA,'r','utf-8').readlines()
	for i in range(len(newsdata)):
		newsdata[i] = newsdata[i].encode('utf-8').decode('utf-8-sig').strip()

	if feature_option == 1:
		corpus = feature1.preprocess_bow(newsdata)
	# extract BOW feature
	if feature_option == 1:
		data_tr_dm = feature1.vectorize_docs( corpus,None, fea_name="BOW")

	#生成feature_tmp-------------------------------------------------------------------
	import codecs
	# get label dict
	label_dict = {}
	with codecs.open('label_ind.txt','r',encoding='utf-8') as label_dict_f:
		label_list = label_dict_f.read().splitlines()
	for i in label_list:
		label_dict[int(i.split('\t')[1])] = i.split('\t')[0]

	file_exist_flag = np.ones(FILE_NUM)

	import jieba

	PATH_TMP = PATH_CURR +'\\tmp\\' + 'data_doc2vec_training'
	PATH_TMP_DICT = os.path.join(PATH_TMP, "dict")
	PATH_SEP_NEWS = PATH_CURR +  "\\news"
	PATH_FEATURE_TMP = PATH_CURR + '\\feature_tmp\\'

	feature_option = 'bow'
	if feature_option == 'bow':
		import pickle
		with open((PATH_TMP_DICT + "\\vocab.dict"), 'rb') as fl:
			dicts = pickle.load(fl)
		from sklearn.feature_extraction.text import TfidfVectorizer
		tv_te = TfidfVectorizer(vocabulary=dicts)
		for item in range(FILE_NUM):
			if file_exist_flag[item] == 0:
				continue
			news_file = codecs.open(PATH_SEP_NEWS + '\\' +  label_dict[item] +'.txt', 'r', 'utf-8')
			one_cat_news = news_file.readlines()
			for i in range(len(one_cat_news)):
				one_cat_news[i] = one_cat_news[i].strip()
			# print(one_cat_news)
			processed_one_cat_corpus_bow = model_train_svm.preprocess_bow(one_cat_news)
			sparce_mat_bow = tv_te.fit_transform(processed_one_cat_corpus_bow)
			# log.info("BOW representation infering Finished")

			scio.savemat((PATH_FEATURE_TMP+str(item)+"_news_bow.mat"),
							{"data_bow": np.array(sparce_mat_bow)
							})

	#生成xgboost训练数据-------------------------------------------------------------------
	from scipy import sparse
	def writeData_balance(allPart):
		
		PATH_DATA = PATH_CURR + '/feature_transformation/'
		PATH_FEATURE = PATH_CURR + '/feature_tmp/'


		for part in range(0,allPart):
			data_X = []
			data_Y = []
			flag = True
			first_flag = True
			for i in range(part*2,part*2+2):
				
				dataFile = PATH_FEATURE + str(i) + '_news_bow.mat'
				data = scio.loadmat(dataFile)
				print( data["data_bow"][0][0].shape)
				
				if flag:
					flag = False
					vector1 = data["data_bow"][0][0]
					target1 = np.repeat(1, vector1.shape[0])
				else:
					vector1 = sparse.vstack([vector1,data['data_bow'][0][0]])
					target1 = np.append(target1, np.repeat(i, data["data_bow"][0][0].shape[0]))

			log.info(vector1.shape)
			#合并
			for i in range(0,vector1.shape[0]):
				for j in range(0,vector1.shape[0]):
					if target1[i] == target1[j]:
						y = 1
					else:
						y = 0
					
					if first_flag:
						first_flag = False
						data_X = sparse.hstack((sparse.coo_matrix.getrow(vector1,i),sparse.coo_matrix.getrow(vector1,j)))
					else:  
						data_X = sparse.vstack([data_X,sparse.hstack((sparse.coo_matrix.getrow(vector1,i),sparse.coo_matrix.getrow(vector1,j)))])
					data_Y.append(y)
				log.info("Processing the "+ str(part*2) + "~"+ str(part*2+1) + " file - "+str(round((i/vector1.shape[0])*100))+"%")
			
			#暂存到pickle中
			with open(PATH_DATA + str(part) + ".pik", "wb") as f:
				tempData = {"x": data_X,"y": data_Y}
				pickle.dump(tempData,f)	

		#将所有的pickle文件读取出来保存
		data_X = []
		data_Y = []
		first_flag = True
		for part in range(0,allPart):
			with open(PATH_DATA + str(part) + ".pik", "rb") as f:
				tempData = pickle.load(f)
			
			#存储到DataX 和 DataY中
			if first_flag:
				first_flag = False
				# data_X = sparse.hstack((sparse.coo_matrix.getrow(vector1,i),sparse.coo_matrix.getrow(vector1,j)))
				data_X = tempData["x"]
			else:  
				data_X = sparse.vstack([data_X,tempData["x"]])
			data_Y = data_Y + tempData["y"]


		log.info(data_X.shape)
		log.info(len(data_Y))
		scio.savemat((PATH_DATA + "newData.mat"), {"x": data_X,"y": data_Y}) 

	FILE_NUM = round(ratio*FILE_NUM)
	writeData_balance(round(FILE_NUM/2))

	#训练模型-------------------------------------------------------------------
	import xgboostModel
	xgboostModel.runModel(modelName, num)

def modelTest(modelName):
	log = logging.getLogger()
	log.setLevel(logging.DEBUG)
	ch = logging.StreamHandler(sys.stdout)
	ch.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	ch.setFormatter(formatter)
	log.addHandler(ch)


	PATH_CURR = os.path.abspath(".")
	PATH_TEST = PATH_CURR + "/data/test/"
	PATH_TMP_DICT = PATH_CURR + "/tmp/data_doc2vec_training/dict/"
	PATH_MODEL = PATH_CURR + "/modelSave/"
	######提取测试集######
	# print(ca)
	for _, _, files in os.walk(PATH_TEST):
		pass
	if len(files) < 2:
		return -1
	with open(PATH_TEST + files[0],"r",encoding="utf-8") as f1:
		newsSet1 = f1.readlines()
	with open(PATH_TEST + files[1],"r",encoding="utf-8") as f2:
		newsSet2 = f2.readlines()

	######提取特征######
	feature_option = 'bow'
	if feature_option == 'bow':
    	#读取词向量
		with open((PATH_TMP_DICT + "/vocab.dict"), 'rb') as fl:
			dicts = pickle.load(fl)
		from sklearn.feature_extraction.text import TfidfVectorizer
		tv_te = TfidfVectorizer(vocabulary=dicts)

		for i in range(len(newsSet1)):
			newsSet1[i]=newsSet1[i].strip()
		processed_one_cat_corpus_bow1 = fea.preprocess_bow(newsSet1)
		sparce_mat_bow1 = tv_te.fit_transform(processed_one_cat_corpus_bow1)

		for i in range(len(newsSet2)):
			newsSet2[i]=newsSet2[i].strip()
		processed_one_cat_corpus_bow2 = fea.preprocess_bow(newsSet2)
		sparce_mat_bow2 = tv_te.fit_transform(processed_one_cat_corpus_bow2)

    ####################

	log.info(sparce_mat_bow1.shape)
	log.info(sparce_mat_bow2.shape)


    ####做笛卡儿积######
	data_x = []
	data_y = []
	first_flag = True

	for i in range(0,sparce_mat_bow1.shape[0]):
		for j in range(0,sparce_mat_bow2.shape[0]):
			if first_flag:
				first_flag = False
				data_x = sparse.hstack((sparse.coo_matrix.getrow(sparce_mat_bow1,i),sparse.coo_matrix.getrow(sparce_mat_bow2,j)))
			else:
				data_x = sparse.vstack([data_x,sparse.hstack((sparse.coo_matrix.getrow(sparce_mat_bow1,i),sparse.coo_matrix.getrow(sparce_mat_bow2,j)))])
			data_y.append(0)
        
		for j in range(0,sparce_mat_bow1.shape[0]):
			if first_flag:
				first_flag = False
				data_x = sparse.hstack((sparse.coo_matrix.getrow(sparce_mat_bow1,i),sparse.coo_matrix.getrow(sparce_mat_bow1,j)))
			else:
				data_x = sparse.vstack([data_x,sparse.hstack((sparse.coo_matrix.getrow(sparce_mat_bow1,i),sparse.coo_matrix.getrow(sparce_mat_bow1,j)))])
			data_y.append(1)
        
		# print(i)
		log.info(i)
	
	for i in range(0,sparce_mat_bow2.shape[0]):
		for j in range(0,sparce_mat_bow2.shape[0]):
			if first_flag:
				first_flag = False
				data_x = sparse.hstack((sparse.coo_matrix.getrow(sparce_mat_bow2,i),sparse.coo_matrix.getrow(sparce_mat_bow2,j)))
			else:
				data_x = sparse.vstack([data_x,sparse.hstack((sparse.coo_matrix.getrow(sparce_mat_bow2,i),sparse.coo_matrix.getrow(sparce_mat_bow2,j)))])
			data_y.append(1)
        
		# print(i)
		log.info(i)

    # print(data_x.shape)

	dtest = xgb.DMatrix(data_x, data_y)
    ####################

	log.info("test")


    #####model##########
    #load model
	with open(PATH_MODEL+modelName,'rb') as modelf:
		model = pickle.load(modelf)
		preds = model.predict(dtest)
		predictions = [round(value) for value in preds]
		
		y_test = dtest.get_label()
		
		# log.info(y_test)
		log.info(preds)
		log.info(predictions)
		# log.info ("y_test："+str(y_test))
		
		test_accuracy = accuracy_score(y_test, predictions)
    
	return test_accuracy