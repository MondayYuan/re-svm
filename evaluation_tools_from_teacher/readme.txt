这是经过修改的评测程序，去除了正式评测程序中的标准答案和测试集，将其替换为了训练数据中的一些数据，用于检查输入格式。

ieproject.jar    测试程序
data文件夹   数据文件夹
|—  task1_input.xml  任务1 测试语料
|— task2_input_cn.xml 任务2 中文测试语料
|— task2_input_en.xml 任务2 英文测试语料
|— task1_output.xml 任务1 语料答案
|— task2_output_cn.xml 任务2中文语料答案
|— task2_output_en.xml 任务2英文语料答案
|— test1.xml 任务1样例结果
|— test2.xml 任务2中文样例结果

测试程序需要两项一起。测试程序执行指令如下：

使用CMD 转到 命令行方式下，制表TAB可以复制当前目录名称。data/test1.xml，data/test2.xml，data/test2.xml 是DATA目录下学生的输出文件。

在IEPROJECT.JAR目录下执行下面语句：

任务一：
java -jar ieproject.jar -1 -f data/test1.xml 

任务二中文：
java -jar ieproject.jar -2 -f data/test2_cn.xml 

任务二英文：
java -jar ieproject.jar -2 -e -f data/test2_en.xml 


JAVA  环境变量设置：http://jingyan.baidu.com/article/215817f7e3f2bd1eda1423f4.html

WIN10 ： 文件资源管理器-》右键此电脑-》属性-》高级系统设置-》环境变量：

JAVA_HOME（新建该环境变量）： JAVA 安装路径

CLASSPATH（新建该环境变量） .;%JAVA_HOME%\lib\dt.jar;%JAVA_HOME%\lib\tools.jar;

PATH       %JAVA_HOME%\bin;%JAVA_HOME%\jre\bin;


