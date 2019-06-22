
from werkzeug.utils import secure_filename
from flask import Flask,render_template,jsonify,request,send_from_directory
from flask import request
from flask import render_template
import numpy as np
from multiprocessing import Pool
import main
import os
import json
import pickle


MODEL_NAME = ""
app = Flask(__name__)

def setModelName(modelName):
    #创建一个pickle来保存当前ModelName
    file_dir = './tmp/modelName.pik'
    with open(file_dir,"wb") as f:
        temp = {"modelName": modelName}
        pickle.dump(temp, f)
        print(temp)

def getModelName():
    #获取当前model
    file_dir = './tmp/modelName.pik'
    with open(file_dir,"rb") as f:
        temp = pickle.load(f)
    return temp["modelName"]

############################################api############################################

#index
@app.route('/', methods=['GET', 'POST'])
def home():
    return "home"
    # return render_template('index.html')


@app.route('/get_sim', methods=['GET', 'POST'])
def get_sim():
    jsonStr = request.form['json']
    jsonStr = json.loads(jsonStr)
    # print(jsonStr)
    # # 测试部分
    # PATH_CURR = os.path.abspath(".")
    # PATH_SEP_NEWS = PATH_CURR +  "\\data\\news\\"

    # for root, dirs, files in os.walk(PATH_SEP_NEWS):
    #     with open(PATH_SEP_NEWS + files[0],"r",encoding="utf-8") as f1:
    #         newsSet1 = f1.readlines()
    #     with open(PATH_SEP_NEWS + files[1],"r",encoding="utf-8") as f2:
    #         newsSet2 = f2.readlines()

    # json = {"1":newsSet1, "2":newsSet2}

    #获取当前model
    file_dir = './tmp/modelName.pik'
    with open(file_dir,"rb") as f:
        temp = pickle.load(f)
    modelName = temp["modelName"]
    if modelName == "停止运行":
        return jsonify({"code":200, "sim":"系统已停止"})
    sim = main.simForNews(jsonStr, modelName)
    return jsonify({"code":200, "sim":sim})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
