from PyQt5.QtWidgets import (QWidget, QProgressBar, QLabel, QHBoxLayout, QVBoxLayout,QLineEdit,QGridLayout,QTextEdit,QComboBox,QDialog,
    QPushButton, QApplication)
from PyQt5.QtCore import QBasicTimer
from PyQt5.QtGui import QFont
import sys
import os
import re
import modelGenerate
import model
import _thread
from multiprocessing import Process

class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    
    def initUI(self):
        # allModel = self.getModel()

        #查询模型
        self.queryModelLabel = QLabel('模型查询')
        self.queryModelLabel.setFont(QFont('SansSerif', 15))
        self.queryModelName = QLabel('查询模型')

        #模型管理
        self.manageModelLabel = QLabel('模型管理')
        self.manageModelLabel.setFont(QFont('SansSerif', 15))
        self.allModelName = QLabel('所有模型')
        self.deleteModelName = QLabel('模型删除')
        
        #模型训练
        self.trainModelLabel = QLabel('模型训练')
        self.trainModelLabel.setFont(QFont('SansSerif', 15))
        self.trainModelName = QLabel('模型名')
        self.trainRatioName = QLabel('训练比率')
        self.trainNumName = QLabel('迭代次数')
        self.trainStartName = QLabel('开始训练')

        #运行模型
        self.runModelLabel = QLabel('运行模型')
        self.runModelLabel.setFont(QFont('SansSerif', 15))
        self.sysStateName = QLabel('系统状态')
        self.selectModelName = QLabel('模型选择')
        self.testModelName = QLabel('模型测试')
        self.runModelName = QLabel('运行系统')
        
        #查询模型-查询模型
        self.queryModelNameEdit = QLineEdit()
        self.queryModelButton = QPushButton("查询")

        #模型管理-加载所有模型
        self.allModelSelect = QComboBox(self)
        # for item in allModel:
        #     self.allModelSelect.addItem(item)
        self.allModelButton = QPushButton("加载")
        
        #模型管理-模型删除
        self.deleteModelSelect = QComboBox(self)
        # for item in allModel:
        #     self.deleteModelSelect.addItem(item)
        self.deleteModelButton = QPushButton("删除")

        #模型训练-模型名
        self.trainModelNameEdit = QLineEdit()
        self.trainRatioNameEdit = QComboBox(self)
        for i in range(1,11):
            self.trainRatioNameEdit.addItem(str(i/10))
        self.trainNumNameEdit = QComboBox(self)
        for i in range(1,11):
            self.trainNumNameEdit.addItem(str(i*100))
        self.trainModelButton = QPushButton("训练")

        #运行模型-选择模型
        self.sysState = QLabel('532532532')
        self.setState()
        self.sysState.setFont(QFont('SansSerif', 10))
        self.runModelSelect = QComboBox(self)
        # for item in allModel:
        #     self.runModelSelect.addItem(item)

        #运行模型-模型测试
        self.testModelNameEdit = QLabel('准确率:')
        self.testModelButton = QPushButton("测试")

        #运行模型-运行系统
        self.runModelButton = QPushButton("运行")
        self.stopModelButton = QPushButton("停止")


        grid = QGridLayout()
        grid.setSpacing(10)

        #模型查询
        grid.addWidget(self.queryModelLabel, 1, 0)
        grid.addWidget(self.queryModelName, 2, 0)
        grid.addWidget(self.queryModelNameEdit, 2, 1)
        grid.addWidget(self.queryModelButton, 2, 2)

        #模型管理
        grid.addWidget(self.manageModelLabel, 3, 0)
        grid.addWidget(self.allModelName, 4, 0)
        grid.addWidget(self.allModelSelect, 4, 1)
        grid.addWidget(self.allModelButton, 4, 2)
        grid.addWidget(self.deleteModelName, 5, 0)
        grid.addWidget(self.deleteModelSelect, 5, 1)
        grid.addWidget(self.deleteModelButton, 5, 2)

        #模型训练
        grid.addWidget(self.trainModelLabel, 6, 0)
        grid.addWidget(self.trainModelName, 7, 0)
        grid.addWidget(self.trainModelNameEdit, 7, 1)
        grid.addWidget(self.trainRatioName, 8, 0)
        grid.addWidget(self.trainRatioNameEdit, 8, 1)
        grid.addWidget(self.trainNumName, 9, 0)
        grid.addWidget(self.trainNumNameEdit, 9, 1)
        grid.addWidget(self.trainStartName, 10, 0)
        grid.addWidget(self.trainModelButton, 10, 1)

        #运行模型
        grid.addWidget(self.runModelLabel, 11, 0)
        grid.addWidget(self.sysStateName, 12, 0)
        grid.addWidget(self.sysState, 12, 1)
        grid.addWidget(self.selectModelName, 13, 0)
        grid.addWidget(self.runModelSelect, 13, 1)
        grid.addWidget(self.testModelName, 14, 0)
        grid.addWidget(self.testModelNameEdit, 14, 1)
        grid.addWidget(self.testModelButton, 14, 2)
        grid.addWidget(self.runModelName, 15, 0)
        grid.addWidget(self.runModelButton, 15, 1)
        grid.addWidget(self.stopModelButton, 15, 2)


        #绑定事件
        self.queryModelButton.clicked.connect(self.queryModel)
        self.allModelButton.clicked.connect(self.loadModel)
        self.trainModelButton.clicked.connect(self.trainModel)
        self.deleteModelButton.clicked.connect(self.deleteModel)
        self.testModelButton.clicked.connect(self.testModel)
        self.runModelButton.clicked.connect(self.runSys)
        self.stopModelButton.clicked.connect(self.stopSys)

        self.setLayout(grid) 

        self.setGeometry(400, 300, 550, 400)
        self.setWindowTitle('Review')    
        self.show()

    
    def queryModel(self):
        #判断是否有输入文件名
        modelName = self.queryModelNameEdit.text()
        if modelName == "":
            self.showDialog("请输入模型名!", "Error")
            return -1
        
        #清空所有
        self.runModelSelect.clear()
        self.allModelSelect.clear()
        self.deleteModelSelect.clear()

        #得到所有的模型名字
        allModel = self.getModel()
        
        #根据输入的模型名来筛选
        pattern=r""+modelName+""
        for item in allModel:
            # print(re.search(pattern,item))
            if re.search(pattern,item) == None:
                continue
            self.runModelSelect.addItem(item)
            self.allModelSelect.addItem(item)
            self.deleteModelSelect.addItem(item)

    def loadModel(self):
        #清空所有
        self.runModelSelect.clear()
        self.allModelSelect.clear()
        self.deleteModelSelect.clear()

        #加载所有模型到下拉列表中
        allModel = self.getModel()
        for item in allModel:
            self.runModelSelect.addItem(item)
            self.allModelSelect.addItem(item)
            self.deleteModelSelect.addItem(item)

    def getModel(self):
        #获取现有模型  
        file_dir = './modelSave/'
        for root, dirs, files in os.walk(file_dir):
            pass
        return files
		
    def deleteModel(self):
        file_dir = './modelSave/'
        #获取待删除的模型名    
        deleteModelName = self.deleteModelSelect.currentText()
        if deleteModelName == "":
            self.showDialog("请先加载模型!", "Error")
            return -1
        deleteModelIndex = self.deleteModelSelect.currentIndex()
        deleteFile = file_dir + deleteModelName
        os.remove(deleteFile)
        #删除列表中的item
        self.deleteModelSelect.removeItem(deleteModelIndex)
        self.runModelSelect.removeItem(deleteModelIndex)
        self.allModelSelect.removeItem(deleteModelIndex)
        self.showDialog('模型"'+deleteModelName+'"删除成功!', "Info")

    def setState(self):
        modelName = model.getModelName()
        if modelName!="停止运行":
            modelName = '模型"'+modelName+'"运行中!'
        self.sysState.setText(modelName)

    def testModel(self):
        modelName = self.runModelSelect.currentText()
        if modelName == "":
            self.showDialog("请先加载模型!", "Error")
            return -1
        
        self.testModelNameEdit.setText('准确率: 正在测试中...')
        #开线程测试
        _thread.start_new_thread(self.testModelThread,(1,))
        self.showDialog('模型"'+modelName+'"正在测试中!', "Info")

    
    def testModelThread(self, id):
        modelName = self.runModelSelect.currentText()
        acc = modelGenerate.modelTest(modelName)
        if acc == -1:
            self.testModelNameEdit.setText('请至少放入两个文件至文件夹"./data/test/"下!')
            return -1
        
        self.testModelNameEdit.setText('模型"'+modelName+'"的准确率: '+str(acc))
        print(acc)

    def trainModel(self):
        #判断是否有输入文件名
        modelName = self.trainModelNameEdit.text()
        modelRatio = self.trainRatioNameEdit.currentText()
        modelNum = self.trainNumNameEdit.currentText()
        if modelName == "":
            self.showDialog("请输入模型名!", "Error")
            return -1
        if modelRatio == "":
            self.showDialog("请输入比率!", "Error")
            return -1
        if modelNum == "":
            self.showDialog("请输入迭代次数!", "Error")
            return -1
        
        #开线程训练
        _thread.start_new_thread(self.trainModelThread,(1,))
        self.showDialog('模型"'+modelName+'"正在训练中!', "Info")
        # try:
        # except:
        #     print("Error: unable to start thread")
    
    def trainModelThread(self, id):
        # print(id)
        modelName = self.trainModelNameEdit.text()
        modelRatio = float(self.trainRatioNameEdit.currentText())
        modelNum = int(self.trainNumNameEdit.currentText())
        print(modelName)
        print(modelRatio)
        print(modelNum)
        modelGenerate.modelGenerate(modelName, modelRatio, modelNum)
        self.showDialog("模型训练完成!", "Info")

    
    def showDialog(self, content, title):
        #创建QDialog对象
        dialog=QDialog()
        lbl1 = QLabel(content, dialog)
        lbl1.move(50, 50)
        dialog.resize(350,300)
        dialog.setWindowTitle(title)
        dialog.exec_()
    

    def runSys(self):
        #获取待运行的模型名    
        runModelName = self.runModelSelect.currentText()
        if runModelName == "":
            self.showDialog("请先加载模型!", "Error")
            return -1
        model.setModelName(runModelName)
        self.showDialog('模型"'+runModelName+'"运行成功!', "Info")
        self.setState()

    def stopSys(self):
        model.setModelName("停止运行")
        self.showDialog("模型停止成功!", "Info")
        self.setState()
            
        
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())