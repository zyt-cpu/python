import json
import urllib.request,urllib.parse
import os
import matplotlib.pyplot as plt
import numpy as np
import cmath
import math
import statsmodels.stats.weightstats as st

#----------------------------------------------------
print("题目难度判断")
#根据提交次数辅助判断
def Upload(case_id,arrays,str):
    if(str=="EM"):
        for i in arrays:
            if (case_id == i[0]):
                if (i[1] <= 5):
                    return True
                else:
                    return False
    elif str=="MH":
        for i in arrays:
            if (case_id == i[0]):
                if (i[1] <= 7):
                    return True
                else:
                    return False

#题目难度统计
def caseNum(value,target):
    mid={}
    total=0
    per_E=0
    per_M=0
    per_H=0
    for key in value:
        if(value[key][0]==target):
            total+=1
            if(value[key][1]=="E"):
                per_E+=1
            elif value[key][1]=="M":
                per_M+=1
            else:
                per_H+=1
    mid["total"]=total
    mid["E"]=per_E
    mid["M"]=per_M
    mid["H"]=per_H
    return mid



with open("test_data.json",'r',encoding='UTF-8') as load_f:
    load_dict = json.load(load_f)
    load_dict = load_dict.items()
    varData = {}
    upload_num={}
    item_num={}

    for key, value in load_dict:
        for data in value['cases']:
            case_id = data['case_id']
            finalScore = data['final_score']

            for vars in data['upload_records']:
                if finalScore != 0:
                    score = vars['score'] / finalScore * 100  # 分数转化
                else:
                    score = float(vars['score'])
                if case_id in varData.keys():
                    varData[case_id][0] += 1
                    varData[case_id].append(score)
                else:
                    varData[case_id] = [1, score]     #转换分制


            for records in data["upload_records"]:    #计算提交次数
                if data["case_id"] not in upload_num:
                    upload_num[data["case_id"]]=1
                else:
                    upload_num[data["case_id"]]+=1
            if data["case_id"] not in item_num:
                item_num[data["case_id"]]=1
            else:
                item_num[data["case_id"]]+=1
    varDict = {}
    avgData = {}
    standardScore = {}
    for avg in varData:
        if varData.get(avg)[0] != 0:
            da = np.array(varData[avg])
            sums = np.sum(da[1:])
            avgScore = sums / float(varData[avg][0])  # 计算平均分
            vars = np.var(da[1:])
            sizeAll = len(da[1:])
            sc = [x for x in da[1:] if x >= 60]
            stand = len(sc) / sizeAll * 100  # 为之后求相关系数准备
        else:
            avgScore = 0.0
            vars = 0.0
            stand = 0.0
        avgData[avg] = avgScore
        varDict[avg] = vars
        standardScore[avg] = stand

    upload = {}     #计算平均提交次数
    for key in upload_num:
        upload[key]=upload_num[key]/item_num[key]

    sortData = sorted(avgData.items(), key=lambda x: x[1], reverse=False)
    passData = sorted(standardScore.items(), key=lambda x: x[1], reverse=False)
    sortUpload=sorted(upload.items(), key=lambda x: x[1], reverse=False)
    print("平均成绩如下所示")
    print(sortData)
    print("平均提交次数如下所示")
    print(sortUpload)
    print("通过率如下所示")
    print(passData)

    #计算平均成绩与通过率之间的协方差
    sum_num=0
    sum_pass=0
    sum_score=0
    P = []  # 通过率数据
    S = []  # 分数数据
    U = []  # 提交数据,放大十倍，观察曲线吻合
    for key in sortData:
        sum_score+=key[1]
        S.append(key[1])
    for key in passData:
        sum_pass+=key[1]
        P.append(key[1])
    for key in sortUpload:
        sum_num+=key[1]
        U.append(key[1]*10)
    avg_upload=sum_num/len(sortData)
    avg_pass=sum_pass/len(passData)
    avg_score=sum_score/len(sortUpload)

    sum_pass_upload=0
    sum_pass_score=0
    sum_pass=0
    sum_score=0
    sum_upload=0

    for i in passData:
        for j in sortUpload:
            if(i[0]==j[0]):
                sum_pass+=math.pow((i[1]-avg_pass),2)
                sum_upload+=math.pow(j[1]-avg_upload,2)
                sum_pass_upload+=(i[1]-avg_pass)*(j[1]-avg_upload);
        for k in sortData:
            if(i[0]==k[0]):
                sum_score+=math.pow(k[1]-avg_score,2)
                sum_pass_score+=(i[1]-avg_pass)*(k[1]-avg_score);
    cov_pass_upload=sum_pass_upload/(len(passData)-1)
    cov_pass_score=sum_pass_score/(len(passData)-1)

    #计算相关系数
    S_pass=cmath.sqrt(sum_pass/(len(passData)-1))
    S_score=cmath.sqrt(sum_score/(len(passData)-1))
    S_upload=cmath.sqrt(sum_upload/(len(passData)-1))
    S_pass_score=cov_pass_score/(S_pass*S_score)
    S_pass_upload=cov_pass_upload/(S_pass*S_upload)
    print("平均分数的相关系数：")
    print(S_pass_score)
    print("平均提交次数的相关系数：")
    print(S_pass_upload)
    if(abs(S_pass_upload)>abs(S_pass_score)):
        print("可以看出：提交次数与通过率的绝对值更接近1，提交次数与通过率的相关性更高")
    else:
        print("可以看出：分数与通过率的绝对值更接近1，分数与通过率的相关性更高")

    x=range(1,883)
    plt.rcParams['font.family'] = ['sans-serif']
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.title("")
    plt.plot(x, S, color='red', label='平均分')
    plt.plot(x, P, color='black', label='通过率')
    plt.plot(x, U, color='blue', label='平均提交次数')
    plt.legend()
    plt.ylabel('难度')
    plt.xlabel('题号（对应题号请看Console输出）')
    plt.show()

#假设检验:双总体均值用t检验方法
i=0
j=0
t,p_two,df=st.ttest_ind(S,P,usevar='unequal')
print('t=',t,'p值：',p_two,'自由度：',df)

alpha=0.05     #使用alpha=5%
if p_two<alpha/2:
    print('拒绝原假设，有显著差异,所以平均分和通过率有显著差异')
else:
    print('接受原假设，没有显著差异，所以平均分和通过率没有显著差异')

print('根据自由度查表，t值为1.96')
t_ci=1.96
se=np.sqrt(np.var(S)/len(S)+np.mean(P)/len(P))

#置信区间的样本平均值=A样本平均值-B样本平均值

sample_mean=np.mean(S)-np.mean(P)
#置信区间上限
a=sample_mean-t_ci*se
#置信区间下限
b=sample_mean+t_ci*se

print('平均分和通过率差值的置信区间，95置信水平 CI=[%f,%f]'%(a,b))

#确定题目难度
print("题目难度确定：H:Hard M:Medium E:Easy")
score_H=[]
score_M=[]
score_E=[]
for i in sortData:
    if(i[1]<=60):
        score_H.append(i[0])
    elif i[1]<=80:
        score_M.append(i[0])
    else:
        score_E.append(i[0])

pass_E=[]
pass_M=[]
pass_H=[]
for i in passData:
    if(i[1]<=45):
        pass_H.append(i[0])
    elif i[1]<=75:
        pass_M.append(i[0])
    else:
        pass_E.append(i[0])

#分数和通过率作为主要判断依据，提交情况进行次要判断依据
#在两个标准中分布两个水平的题目，根据提交次数进一步分类

final_H=[]
final_M=[]
final_E=[]
for i in score_E:
    if i in pass_E:
        final_E.append(i)
    elif i in pass_M:
        if Upload(i,sortUpload,"EM"):
            final_E.append(i)
        else:
            final_M.append(i)
    else:
        final_M.append(i)
for i in score_M:
    if i in pass_E:
        if Upload(i,sortUpload,"EM"):
            final_E.append(i)
        else:
            final_M.append(i)
    elif i in pass_M:
        final_M.append(i)
    else:
        if Upload(i, sortUpload,"MH"):
            final_M.append(i)
        else:
            final_H.append(i)
for i in score_H:
    if i in pass_E:
        final_M.append(i)
    elif i in pass_M:
        if Upload(i, sortUpload,"MH"):
            final_M.append(i)
        else:
            final_H.append(i)
    else:
        final_H.append(i)

print("E")
print(final_E)
print("M")
print(final_M)
print("H")
print(final_H)

#汇总视图：柱状图
plt.subplot(121)
# 柱子总数
N = 3
# 包含每个柱子对应值的序列
values = (len(final_E),len(final_M),len(final_H))
# 包含每个柱子下标的序列
index = np.arange(N)
# 柱子的宽度
width = 0.45
# 绘制柱状图, 每根柱子的颜色为紫罗兰色
p2 = plt.bar(index, values, width,  color="#87CEFA")
# 设置横轴标签
plt.xlabel('题目难度')
# 设置纵轴标签
plt.ylabel('题数')
# 添加标题
plt.title('题目难度汇总')
# 添加纵横轴的刻度
plt.xticks(index, ('E', 'M', 'H'))
# plt.yticks(np.arange(0, 10000, 10))
# 添加图例
plt.legend(loc="upper right")
#添加数据标签
plt.text(0, len(final_E)+14, len(final_E), ha='center', va='top', fontsize=10,rotation=0)
plt.text(1, len(final_M)+14, len(final_M), ha='center', va='top', fontsize=10,rotation=0)
plt.text(2, len(final_H)+14, len(final_H), ha='center', va='top', fontsize=10,rotation=0)

#比例视图：饼状图
plt.subplot(122)
labels='E','M','H'
sizes=len(final_E),len(final_M),len(final_H)
colors='lightgreen','gold','lightskyblue'
element="E:Easy","M:Medium","H:Hard"
explode=0.1,0.1,0.1
wedges,texts,autotexts=plt.pie(sizes,explode=explode,labels=labels,
        colors=colors,autopct='%1.1f%%',shadow=True,startangle=50)
plt.legend(wedges,element,fontsize=7,title="含义说明",loc="upper right")
plt.title("题目难度比例")
plt.axis('equal')
plt.show()
#------------------------------------------------
print("答题人水平判断(根据每人的答题粗略判断)")

cases={}
for key,value in load_dict:
    case={}
    for data in value["cases"]:
        str=""
        #题目难度
        if data["case_id"] in final_E:
            str+="E"
        elif data["case_id"] in final_M:
            str+="M"
        else:
            str+="H"
        #分数难度
        if data["final_score"]<60:
            str+="H"
        elif data["final_score"]<80:
            str+="M"
        else:
            str+="E"
        #提交次数
        count=0
        for i in data["upload_records"]:
            count+=1
        if count<=5:
            str+="E"
        elif count<=7:
            str+="M"
        else:
            str+="H"
        case[data["case_id"]]=str
    cases[value["user_id"]]=case
print()
print("各人答题情况：第一个是题目难度，第二个是分数，第三个是提交次数")
print("分数:<60位H，<80为M，>=80为E")
print("提交次数：<=5为E，<=7为M，>7为H")
print(cases)

#难度比例
num_result={}
for key in cases:
    mid={}
    result={}
    mid["E"]=caseNum(cases[key],"E")
    mid["M"]=caseNum(cases[key],"M")
    mid["H"]=caseNum(cases[key],"H")
    result["user_id"]=key
    result["cases"]=mid
    num_result[key]=result
print("各人答题数量情况：")
print(num_result)

#例子数据饼状图实例
test=num_result[49823]["cases"]

fig=plt.figure()
ax1=fig.add_subplot(2,2,1)
labels='E','M','H'
sizes=test["E"]["E"]/test["E"]["total"],test["E"]["M"]/test["E"]["total"],test["E"]["H"]/test["E"]["total"]
colors='lightgreen','gold','lightskyblue'
explode=0.1,0.1,0.1
ax1.pie(sizes,explode=explode,labels=labels,
        colors=colors,autopct='%1.1f%%',shadow=True,startangle=50)
plt.title("E题目比例")

ax2=fig.add_subplot(2,2,2)
labels='E','M','H'
sizes=test["M"]["E"]/test["M"]["total"],test["M"]["M"]/test["M"]["total"],test["M"]["H"]/test["M"]["total"]
colors='lightgreen','gold','lightskyblue'
element="E:Easy","M:Medium","H:Hard"
explode=0.1,0.1,0.1
wedges,text,autotexts=ax2.pie(sizes,explode=explode,labels=labels,
        colors=colors,autopct='%1.1f%%',shadow=True,startangle=50)
ax2.legend(wedges,element,title="含义说明",fontsize=7,loc="upper right",bbox_to_anchor=(1.1,0,0.3,1))
plt.title("M题目比例")

ax3=fig.add_subplot(2,2,3)
labels='E','M','H'
sizes=test["H"]["E"]/test["H"]["total"],test["H"]["M"]/test["H"]["total"],test["H"]["H"]/test["H"]["total"]
colors='lightgreen','gold','lightskyblue'
explode=0.1,0.1,0.1
ax3.pie(sizes,explode=explode,labels=labels,
        colors=colors,autopct='%1.1f%%',shadow=True,startangle=50)
plt.title("H题目比例")
plt.axis('equal')
plt.suptitle("以49823号答题人为例")
plt.show()

#所有答题者情况汇总

user_E=[]
user_M=[]
user_H=[]
user_O=[]
for key in num_result:
    data=num_result[key]
    if(data["cases"]["H"]["total"]!=0):
        if (data["cases"]["H"]["E"]/data["cases"]["H"]["total"]>0.9) | ((data["cases"]["H"]["E"]/data["cases"]["H"]["total"]>0.6) & (data["cases"]["H"]["M"]/data["cases"]["H"]["total"]>0.3)):
            user_O.append(key)
            continue
    if(data["cases"]["M"]["total"]!=0):
        if (data["cases"]["M"]["E"]/data["cases"]["M"]["total"]>0.9) | ((data["cases"]["M"]["E"]/data["cases"]["M"]["total"]>0.6) & (data["cases"]["M"]["M"]/data["cases"]["M"]["total"]>0.3)):
            user_H.append(key)
            continue
    if(data["cases"]["E"]["total"]!=0):
        if(data["cases"]["E"]["E"]/data["cases"]["E"]["total"]>0.9) | ((data["cases"]["E"]["E"]/data["cases"]["E"]["total"]>0.6) & (data["cases"]["E"]["M"]/data["cases"]["E"]["total"]>0.3)):
            user_M.append(key)
            continue
        else:
            user_E.append(key)
print("在E水平中的答题者：")
print(user_E)
print("在M水平中的答题者：")
print(user_M)
print("在H水平中的答题者：")
print(user_H)
print("对于这些答题者，题目基本中偏下：")
print(user_O)

#汇总视图：柱状图
plt.subplot(121)
# 柱子总数
N = 4
# 包含每个柱子对应值的序列
values = (len(user_E),len(user_M),len(user_H),len(user_O))
# 包含每个柱子下标的序列
index = np.arange(N)
# 柱子的宽度
width = 0.45
# 绘制柱状图, 每根柱子的颜色为紫罗兰色
p2 = plt.bar(index, values, width,  color="#87CEFA")
# 设置横轴标签
plt.xlabel('答题者水平')
# 设置纵轴标签
plt.ylabel('人数')
# 添加标题
plt.title('答题者水平汇总')
# 添加纵横轴的刻度
plt.xticks(index, ('E', 'M', 'H', 'O'))
# plt.yticks(np.arange(0, 10000, 10))
# 添加图例
plt.legend(loc="upper right")
#添加数据标签
plt.text(0, len(user_E)+5, len(user_E), ha='center', va='top', fontsize=10,rotation=0)
plt.text(1, len(user_M)+5, len(user_M), ha='center', va='top', fontsize=10,rotation=0)
plt.text(2, len(user_H)+5, len(user_H), ha='center', va='top', fontsize=10,rotation=0)
plt.text(3, len(user_O)+5, len(user_O), ha='center', va='top', fontsize=10,rotation=0)

#比例视图：饼状图
plt.subplot(122)
labels='E','M','H','O'
elements="E:Easy","M:Medium","H:hard","O:Others"

sizes=len(user_E),len(user_M),len(user_H),len(user_O)
colors='lightgreen','gold','lightskyblue','red'
explode=0.1,0.1,0.1,0.1
wedges,texts,autotexts=plt.pie(sizes,explode=explode,labels=labels,
        colors=colors,autopct='%1.1f%%',shadow=True,startangle=50)
plt.legend(wedges,elements,fontsize=7,title="含义说明",loc="upper right",bbox_to_anchor=(0.91,0,0.3,1))
plt.title("水平分布比例")
plt.axis('equal')
plt.show()
