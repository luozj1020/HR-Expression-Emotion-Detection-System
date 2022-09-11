# 心率-表情情绪识别系统

## 介绍

​		实现情感识别的途径有多种，因为情感会反映在人的各个方面，比如表情、语言、心率等。以目前较为发达的人工智能技术，基于表情、语言等的情感识别技术已经较为成熟，但对于某些特殊情况，例如假表情等的情感识别效果仍然不佳，尽管近年来微表情识别技术有了一定的发展，但由于训练数据的缺乏、单一以及算法的缺陷，大多数识别效果或是泛化性能不佳，缺乏实用价值；而心率不同于表情和语言，大脑不易主动控制，并且早年间已经证实心率会受情绪的影响（比如Myrtek等人，1988），但将心率用于情绪识别的问题是，心率也会受身体运动等因素的影响，并且与受试者的身体各指标息息相关。基于上述分析，要实现较为精确的情感识别，心率和表情是一对互补的指标，并且相对较为容易获取和处理。而要实现基于心率和表情的多模态情感识别，对于表情识别，可以套用[现成算法](https://github.com/atulapra/Emotion-detection)；而对于心率，针对目标是相对静态的办公人群，需要建立算法判断情绪波动，并能够与用户交互以获取用户信息。

## 算法与模型

### 表情识别

首先，用**haar cascade**方法在摄像头识别面部

然后，包含面部的图片将被转化成$48\times48$的矩阵作为CNN的输入

神经网络将会在七种表情中反馈softmax分数

得分最高的表情将显示在平面上

### 心率

​		根据Yang等人[2017]的研究，得到了一个反应心率和表情关系的模型，并考虑了运动对心率的影响，但由于我们面向的用户从事的基本上是室内办公，对于模型中运动的相关参数均设为0.

​		首先，考虑维持人体机能运行需要的心率：
$$
HR_{demand}=(HR_{max}-HR_{min})\times I_{intensity}+HR_{min}
$$
​		其中，$HR_{min}$和$HR_{max}$分别为人体的最低和最高心率，$I_{intensity}$是反映运动的参数，我们设为0，于是
$$
HR_{demand}=HR_{min}
$$
​		$HR_{max}$与人的年龄有关，关系式为$HR_{max}=220-age$

​		$HR_{min}$与人的总体心血管情况有关，且对于生理男性和生理女性受影响不同

​		对于生理男性：
$$
HR_{min}=\dfrac{35}{\lambda}
$$
​		对于生理女性：
$$
HR_{min}=\dfrac{35}{\lambda}+5
$$
​		其中$\lambda$为总体心血管状况，$0<\lambda\le 1$

​		已知上述信息和此刻用户的心率就可以预测下一个时间点的心率：
$$
\hat{HR}(t+1)=HR_{demand}+[HR(t)-HR_{demand}]\times e^{-a\lambda}
$$
​		其中$a$为常数，$a=0.0003$

​		记$AHR=HR-\hat{HR}$，即实际心率与预测心率之差

​		再记$AHR=\dfrac{|AHR|}{HR_{max}-HR_{min}}$

​		最后可以计算精神激活等级(mental arousal level,MAL)来反映是否出现情绪波动
$$
MAL=sign(AHR)\times\dfrac{1-e^{-AHR'}}{1-e^{-1}}
$$
​		MAL范围再-1到1之间，在没有情绪波动时，范围一般再-0.3到0.5之间

​		基于该模型，除了需要获取用户的心率外，我们还需要获取年龄、性别和最低心率或总体心血管情况三个用户个人信息。

## 流程

进入程序会跳出帮助窗口，提示用户输入需要获取的参数的范围

![[QQ截图20220911232322](E:\IGEM\pictures\QQ截图20220911232322.png)
](https://github.com/luozj1020/HR-Expression-Emotion-Detection-System/blob/main/pictures)
关闭帮助窗口后会进入主窗口，用户仍然可以点击主窗口右下角的帮助按钮获取帮助

![QQ截图20220911232700](E:\IGEM\pictures\QQ截图20220911232700.png)

当用户为输入参数或参数有误时，会弹出警告窗口

![QQ截图20220911232736](E:\IGEM\pictures\QQ截图20220911232736.png)

当用户正确输入参数后，点击开始按钮会弹出隐私保护声明按钮，请用户确认允许使用摄像头，并声明输入的信息会经过加密，并不会保存

![QQ截图20220911233032](E:\IGEM\pictures\QQ截图20220911233032.png)

用户接受后，识别程序开始运行，会主窗口会显示心率（程序目前心率采用随机数），同时弹出摄像头窗口和显示实时MAL的窗口，在MAL窗口会显示识别的情绪

![QQ截图20220911233233](E:\IGEM\pictures\QQ截图20220911233233.png)

## 隐私保护与安全

### 权限获取声明

​		摄像头权限是整个程序中涉及隐私保护的最敏感部分，尽管这只是个本地应用程序，信息并不会通过互联网直接泄露到他人手中，但可能会引起用户个人空间被侵犯的感觉二引起不适，因此在程序中需要用到摄像头的部分，我们会向用户告知，并申请权限。

### 个人信息保护

​		由于模型需要获取用户的个人信息，出于对用户个人信息的隐私保护，程序参数基本上实现了闭环传输，基本上不存在会被他人监听的情况。尽管如此，在参数传输过程中，我们仍对用户参数进行了加密处理，使用了1024位的RSA加密体系，并且不会在本地保存公钥和私钥，并在程序运行结束时自动销毁，从而实现了更加严密的隐私保护。

### 输入的合法性

​		考虑到用户可能尝试使程序运行出现bug，对各参数的范围都进行了严格的要求，并且用户输入超出范围或者输入的不是数字的情形，都会跳出警告弹窗。同时，为了防止用户“注入”的操作，我们在最后参数传递时使用了`ast`库的`literal_eval()`函数来预防可能的不当操作。

## 参考资料

Zhaofang Yanga, Wenyan Jiab, Guangyuan Liuc, Mingui Sun: Quantifying mental arousal levels in daily living using additional
heart rate, 2017

Anne-Marie Brouwer, Elsbeth van Dam, Jan B. F. van Erp , Derek P. Spangler and Justin R. Brooks: Improving Real-Life Estimates of
Emotion Based on Heart Rate: A Perspective on Taking Metabolic Heart Rate Into Account, 2018

I Goodfellow, D Erhan, PL Carrier, A Courville, M Mirza, B Hamner, W Cukierski, Y Tang, DH Lee, Y Zhou, C Ramaiah, F Feng, R Li,
X Wang, D Athanasakis, J Shawe-Taylor, M Milakov, J Park, R Ionescu, M Popescu, C Grozea, J Bergstra, J Xie, L Romaszko, B Xu, Z Chuang, and Y. Bengio: Challenges in Representation Learning: A report on three machine learning contests., 2013
