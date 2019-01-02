Relation Extraction Based on SVM
===================
This  is the last project of our course: Internet-based Information Extraction. We need to extract all employee relations from a text.

## Configure Environment

1. install anaconda3

2. create a new environment with python2.7 in anaconda

   * `conda create -n re-py27 python=2.7`
  
   * `conda activate re-py27`
  
3. install pyltp

   * `pip install pyltp`  **(会自动编译，所以会花十来分钟)**

4. [download](http://ltp.ai/download.html) LTP 3.4 model for pyltp  
    把模型解压到项目文件夹下，并重命名为ltp_data
  
5. install libsvm  
   *linux 平台无法使用conda/pip直接安装，也无法通过wheel文件安装，windows平台可以通过wheel安装*
   * download source code
     * `git clone` [https://github.com/cjlin1/libsvm](https://github.com/cjlin1/libsvm)
   * compile
     * `cd libsvm`
     * `make`
     * `cd python`
     * `make`
   * copy files to re-py27 environment
     * copy 
       * libsvm/python/commonutil.py
       * libsvm/python/svm.py
       * libsvm/python/svmtil.py
      
       to **/home/zhouyiyuan/anaconda3/envs/re-py27/lib/python2.7/**  
    * copy **libsvm/libsvm.so.2** to **/home/zhouyiyuan/anaconda3/envs/re-py27/lib/**
6. [download](https://github.com/Embedding/Chinese-Word-Vectors) Chinese word vectors list
   * choose any one txt file from the github, then make a new dir and extract the txt file there 
      * `mkdir word_list`
      * `mv \your path\download_wordlist.txt \word_list`
   
## Function
- pyltp  
  *用于分词/词性标注/命名实体识别*
  - 教程 [https://www.jianshu.com/p/f78453f5d1ca](https://www.jianshu.com/p/f78453f5d1ca)
  - 在线文档 [https://pyltp.readthedocs.io/zh_CN/latest/api.html](https://pyltp.readthedocs.io/zh_CN/latest/api.html)  
  - 标注规则 [https://ltp.readthedocs.io/zh_CN/latest/appendix.html#id4](https://ltp.readthedocs.io/zh_CN/latest/appendix.html#id4)
  
- libsvm  
  *svm api: 训练，预测， 读取数据*
   - 教程 [https://www.cnblogs.com/Finley/p/5329417.html](https://www.cnblogs.com/Finley/p/5329417.html)
   
## Use Steps  

1. run the following command to train and test:

  ` bash train_and_test.sh`

2. to train only:

   `bash train.sh`

3. to test only:

    `bash test.sh`

## Pipeline

- train

![image](https://github.com/MondayYuan/re-svm/raw/master/image/train.png)

- test

![image](https://github.com/MondayYuan/re-svm/raw/master/image/test.png)

- feature extraction

![image](https://github.com/MondayYuan/re-svm/raw/master/image/feature_example.png)

