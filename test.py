import main
import os
import pickle


PATH_CURR = os.path.abspath(".")
PATH_SEP_NEWS = PATH_CURR +  "\\data\\news\\"

for root, dirs, files in os.walk(PATH_SEP_NEWS):  
	with open(PATH_SEP_NEWS + files[0],"r",encoding="utf-8") as f1:
		newsSet1 = f1.readlines()
	with open(PATH_SEP_NEWS + files[1],"r",encoding="utf-8") as f2:
		newsSet2 = f2.readlines()

json = {"1":newsSet1, "2":newsSet2}

#Function Name      : simForNews 
#Function Parameter ：json {"1":newsSet1,"2":newsSet2}
'''
{
    "1":[
            "news1",
            "news2",
            "news3",
            ...
    ],
    "2":[
            "news1",
            "news2",
            "news3",
            ...
    ]
}
'''
#Function return    ：sim(sim for both set), preds (sim for each news from both set)
file_dir = './tmp/modelName.pik'
with open(file_dir,"rb") as f:
	temp = pickle.load(f)
modelName = temp["modelName"]
sim = main.simForNews(json, modelName)

print(sim)