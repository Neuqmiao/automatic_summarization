# -*- coding:utf-8 -*-
import os
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import jieba
import tqdm
import time


jieba.add_word("TAG_NAME_EN")
jieba.add_word("TAG_NUMBER")
jieba.add_word("TAG_DATE")

#  将原始文本转化成为标题|||内容的格式
def read(file_path,file_out_path):
    regression_title = "<contenttitle>"
    regression_title_ = "</contenttitle>"
    regression_content = "<content>"
    regression_content_ = "</content>"
    processed_data = []
    for dirpath, _, filenames in os.walk(file_path):
        for filename in (x for x in sorted(filenames) if x.endswith('.txt')):
            db_path = os.path.join(dirpath, filename)
            with open(db_path,"r") as f:
                data = f.read()
                data = data.decode('gb18030')
                data = data.split("\n")
                for i in range(len(data)):
                    if data[i].startswith(regression_title):
                        title = data[i].replace(regression_title, "")
                        title = title.replace(regression_title_, "")
                        content = data[i+1].replace(regression_content, "")
                        content = content.replace(regression_content_, "")
                        if title and content:
                            processed_data.append(title+"|||"+content)
                        i = i+2
    with open(file_out_path,"w") as f_w:
        for line in processed_data:
            f_w.write(line.encode("utf-8")+"\n")
    print(len(processed_data))


def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code == 12288:                              #全角空格直接转换
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374): #全角字符（除空格）根据关系转化
            inside_code -= 65248
        rstring += unichr(inside_code)
    return rstring
def p(s):
    s1 = strQ2B(s.decode())
    p = re.compile('[()]',re.S)
    s1 = p.sub('',s1)
    return s1.encode("utf-8")
# 将数据中标题长度小于6的删除，将答案中长度小于8的删除
def obtain_length_data(file_path, file_out_path):
    new_data = []
    with open(file_path,"r") as f:
        for line in f:
            line_new = p(line)
            line_split = line_new.split("|||")
            if len(line_split)==2 and len(line_split[0])>13 and len(line_split[1])>22:
                new_data.append(line_new)
    with open(file_out_path,"w") as f_w:
        for line in new_data:
            f_w.write(line.replace("\n","")+"\n")
    print("done")
# 将标题中含有图组：、图文：、<<上一页 下一页>>、跳转至:页、大图欣赏图片名: 上传网友: 图片故事: 图片来源:的进行删除。
def replace_data(file_path, file_out_path):
    new_data = []
    with open(file_path,"r") as f:
        for line in f:
            line =  line.replace("组图:","")
            line = line.replace("图文:","")
            line = line.replace("跳转至:页","")
            line = line.replace("<<上一页 下一页>><<上一页 下一页>>","")
            line = line.replace("大图欣赏图片名: 上传网友: 图片故事: 图片来源:","")
            line = line.replace("大图欣赏图片名: 上传网友:","")
            line = line.replace("标题: 注意:请勿在帖子标题中使用html代码,标题长度不能超过120个字内容:","")
            line = line .replace("来源:","")
            mat_test = re.search(r"\[图\d\]",line)
            if mat_test:
                line = line.replace(mat_test.group(0),"")
            mat_test_ = re.search(r"\d{1,2}\/\d{1,2}", line)
            if mat_test_:
                line = line.replace(mat_test_.group(0),"")
            new_data.append(line)
    with open(file_out_path,"w") as f_w:
        for line in new_data:
            line_split = line.split("|||")
            if len(line_split) == 2 and len(line_split[0]) > 13 and len(line_split[1]) > 22:
                f_w.write(line.replace("\n","")+"\n")
    print("done")
#     给数据打上TAG_NAME_EN、TAG_NUMBER、TAG_DATE的标签。

def label_english(file_path):
    print("start the english")
    start_time = time.time()
    new_data = []
    with open(file_path,"r") as f:
        for line in f:
            mat_english = re.findall(r'([a-zA-Z][a-zA-Z\d]+)', line)
            if mat_english:
                for temp in mat_english:
                    # print(temp)
                    line = line.replace(temp, "TAG_NAME_EN")
            new_data.append(line)
    print("end the english")
    print("The english label time is {}".format(time.time()-start_time))
    return new_data
def lable_date(new_data):
    print("start the date")
    start_time = time.time()
    data_label = []
    for line in new_data:
        # 时间的设置
        mat_date = re.findall(
            r"((\d+·\d+)|((\d{4}年)?\d{1,2}月\d{1,2}日(\d{1,2}(时|点))?((\d{1,2}分)(钟)?)?|(\d{1,2}(时|点)(\d{1,2}分(钟)?)?)|(\d{1,2}(时|点))?\d{1,2}分)|(\d{4}年)|(\d{1,2}(\.|:)\d{1,2}-\d{1,2}(\.|:)\d{1,2}))",
            line)
        if mat_date:
            for temp in mat_date:
                line = line.replace(temp[0], "TAG_DATE")
        data_label.append(line)
    print("end the date")
    print("The date label time is {}".format(time.time()-start_time))
    return data_label

def label_number(data_label,file_out_path):
    new_data = []
    print("start the number")
    start_time = time.time()
    for line in data_label:
        mat_number = re.findall(r"(((\d+)秒(\d+))|(\d+(\.|-)?\d*(点|%)?)|((\d{1,2}-\d{1,2})+))", line)
        if mat_number:
            for temp in mat_number:
                # print(temp[0])
                line = line.replace(temp[0], "TAG_NUMBER")
        new_data.append(line)
    with open(file_out_path, "w") as f_w:
        for temp in new_data:
            f_w.write(temp.replace("\n", "") + "\n")
    print("end the number")
    print("The number label time is {}".format(time.time()-start_time))
    print("done")

def separate_data(file_path,file_out_path):
    index = 0
    data = []
    number_count = 0
    with open(file_path,"r") as f:
        for line in f:
            if index<5000:
                data.append(line)
                index +=1
            else:
                with open(file_out_path+str(number_count)+".txt","w") as f_w:
                    for line in data:
                        f_w.write(line.replace("\n","")+"\n")
                    print("The number {} is succeed".format(number_count))
                    number_count +=1
                data = []
                index = 0
        with open(file_out_path + str(number_count) + ".txt", "w") as f_w:
            for line in data:
                f_w.write(line.replace("\n", "") + "\n")
            print("The number {} is succeed".format(number_count))






def label_data(file_path, file_out_path):
    new_data = []
    with open(file_path,"r") as f:
        for line in f:
            # 时间的设置
            mat_date = re.findall(
                r"((\d+·\d+)|((\d{4}年)?\d{1,2}月\d{1,2}日(\d{1,2}(时|点))?((\d{1,2}分)(钟)?)?|(\d{1,2}(时|点)(\d{1,2}分(钟)?)?)|(\d{1,2}(时|点))?\d{1,2}分)|(\d{4}年)|(\d{1,2}(\.|:)\d{1,2}-\d{1,2}(\.|:)\d{1,2}))",
                line)
            if mat_date:
                for temp in mat_date:
                    line = line.replace(temp[0],"TAG_DATE")
            #设置英文单词
            mat_english = re.findall(r'([a-zA-Z][a-zA-Z\d]*)', line)
            if mat_english:
                for temp in mat_english:
                    # print(temp)
                    line = line.replace(temp, "TAG_NAME_EN")
#             数字的设置
            mat_number = re.findall(r"(((\d+)秒(\d+))|(\d+(\.|-)?\d*(点|%)?)|((\d{1,2}-\d{1,2})+))", line)
            if mat_number:
                for temp in mat_number:
                    # print(temp[0])
                    line = line.replace(temp[0],"TAG_NUMBER")

            new_data.append(line)
    with open(file_out_path,"w") as f_w:
        for temp in new_data:
            f_w.write(temp.replace("\n","")+"\n")
    print("done")

# 将文本进行分词处理,并且的到字典
def segmentation(file_path, file_out_path):
    new_data = []
    with open(file_path,"r") as f:
        for line in f:
            line_split = line.split("|||")
            if len(line_split)==2:
                words_title = jieba.cut(line_split[0])
                title = " ".join(word for word in words_title)
                words_content = jieba.cut(line_split[1])
                content = " ".join(word for word in words_content)
                new_data.append(title+"|||"+content)
    # 写入分词结果
    with open(file_out_path,"w") as f_w:
        for line_one in new_data:
            f_w.write(line_one.replace("\n","")+"\n")

# 得到全部词语的字典
def get_vocabulary(file_path, file_out_vocab):
    data_vocabulary = set()
    with open(file_path,"r") as f:
        for line in f:
            line_split = line.split("|||")
            if len(line_split)==2:
                words_title = line_split[0].split()
                for word in words_title:
                    data_vocabulary.add(word)
                words_content = line_split[1].split()
                for word in words_content:
                    data_vocabulary.add(word)
    # 写入字典结果
    with open(file_out_vocab, "w") as f_v:
        for word in data_vocabulary:
            f_v.write(word + "\n")
    print("done")


def read_separate(file_path):
    train_data = []
    test_data = []
    dev_data = []
    index =0
    with open(file_path,"r") as f:
        for line in f:
            if index<10:
                dev_data.append(line)
                index +=1
            elif index<20:
                test_data.append(line)
                index += 1
            else:
                train_data.append(line)
                index += 1
    return train_data,dev_data,test_data
def title_content_separate(data):
    content = []
    title = []
    for line in data:
        line_split = line.split("|||")
        if len(line_split)==2:
            title.append(line_split[0])
            content.append(line_split[1])
    return title, content

def write(file_out_path,data):
    with open(file_out_path,"w") as f_w:
        for line in data:
            f_w.write(line.replace("\n","")+"\n")

def pipeline_separate(file_path,file_out_path):
    print("Start the separate the data")
    train_data, dev_data, test_data = read_separate(file_path)
    print("Start the separate the title and content")
    title_train, content_train = title_content_separate(train_data)
    print("Start write the train data")
    write(file_out_path+"title-train.txt", title_train)
    write(file_out_path + "content-train.txt", content_train)
    print("Strat write the dev data")
    title_dev, content_dev = title_content_separate(dev_data)
    write(file_out_path+"title-dev.txt", title_dev)
    write(file_out_path + "content-dev.txt", content_dev)
    print("Start write the test data")
    title_test, content_test = title_content_separate(test_data)
    write(file_out_path+"title-test.txt", title_test)
    write(file_out_path + "content-test.txt", content_test)
    print("end")










if __name__=="__main__":
    # 将原始文本转化成为标题|||内容的格式
    # file_path ="data/SogouCS.reduced (1)"
    # file_out_path = "data/news_content.txt"
    # read(file_path,file_out_path)

    # # 将数据中标题长度小于6的删除，将答案中长度小于8的删除
    # file_path = "data/news_content.txt"
    # file_out_path = "data/news_content_length.txt"
    # obtain_length_data(file_path, file_out_path)
    #
    # # 将标题中含有图组：、图文：、<<上一页 下一页>>、跳转至:页、大图欣赏图片名: 上传网友: 图片故事: 图片来源:的进行删除。
    # file_path_ = "data/news_content_length.txt"
    # file_out_path_ = "data/news_content_replace.txt"
    # replace_data(file_path_, file_out_path_)


    #将数据进行拆分
    # file_path = "data/news_content_replace.txt"
    # file_out_path = "data/data_separation/"
    # separate_data(file_path, file_out_path)

    #  给数据打上TAG_NAME_EN、TAG_NUMBER、TAG_DATE的标签。
    # file_path = "data/news_content_replace.txt"
    # file_out_path = "data/news_content_label.txt"
    # new_data = label_english(file_path)
    # data_label = lable_date(new_data)
    # label_number(data_label, file_out_path)
    # print("end")

    # 给小部分数据打上TAG_NAME_EN、TAG_NUMBER、TAG_DATE的标签
    # file_path = "data/data_separation/0.txt"
    # file_out_path = "data/data_separation/label_0.txt"
    # start_time = time.time()
    # new_data = label_english(file_path)
    # data_label = lable_date(new_data)
    # label_number(data_label, file_out_path)
    # end_time = time.time()
    # print(end_time-start_time)


    # 将文本进行分词处理
    # file_path = "data/news_content_label.txt"
    # file_out_path = "data/news_content_segmentation.txt"
    # segmentation(file_path, file_out_path)

    # 将字典进行保存
    # file_path = "data/news_content_segmentation.txt"
    # file_out_vocabulary = "data/vocabulary.txt"
    # get_vocabulary(file_path, file_out_vocabulary)
    # print("done")

    # 将数据进行切分
    start_time = time.time()
    file_path = "data/news_content_segmentation.txt"
    file_out_path = "data/train_data/"
    pipeline_separate(file_path, file_out_path)
    print("The elapsed time is {}".format(time.time()-start_time))

    # 测试分词增加到字典
    # line = "九寨沟美景|||游狐地带[TAG_NAME_EN]: 图片故事: 摄影:王毅刚[搜狐旅游]相关内容"
    # words_title = jieba.cut(line)
    # for word in words_title:
    #     print(word)
    # print(" ".join(word for word in words_title))

    # 测试分词结果
    # line = "九寨沟美景|||游狐地带[TAG_NAME_EN]: 图片故事: 摄影:王毅刚[搜狐旅游]相关内容"
    # line_split = line.split("|||")
    # words_title= jieba.cut(line_split[0])
    # print(" ".join(word for word in words_title))
    # words_content = jieba.cut(line_split[1])
    # print(" ".join(word for word in words_content))

    # badcase test
    # line_badcase = "S*ST湖科正式宣布终止重组退出股改,她以6-72/7-63/10-8险胜法国老将德切,yatou117图片故事: 相关内容"
    # # line_badcase = "yatou117图片故事:"
    # mat_english = re.findall(r'(\b[a-zA-Z][a-zA-Z\d]*\b)',line_badcase)
    # mat_english = re.findall(r"((\d{1,2}-\d{1,2})+)",line_badcase)
    # if mat_english:
    #     for temp in mat_english:
    #         print(temp[0])
    #         print(type(temp))




    # line = "6月24日3时5分,6月24日下午,6月24日下午6月10日0点,02:45,9时15分，8时, 2017年,6.13-6.15北美票房,6月22日15:00-16:00,凌晨2点45分陈瑜“6·26”国际禁毒日到来之际"
    # mat_date = re.findall(r"((\d+·\d+)|((\d{4}年)?\d{1,2}月\d{1,2}日(\d{1,2}(时|点))?((\d{1,2}分)(钟)?)?|(\d{1,2}(时|点)(\d{1,2}分(钟)?)?)|(\d{1,2}(时|点))?\d{1,2}分)|(\d{4}年)|(\d{1,2}(\.|:)\d{1,2}-\d{1,2}(\.|:)\d{1,2}))", line)
    # if mat_date:
    #     for temp in mat_date:
    #         print(temp[0])
    #         print(type(temp))
    # line_number = "福彩3D第08148期,波胆1-1或0-0,16.0%,2900点,大涨101.99点,3700亿,16.0%,9秒90,9秒90,,2-0领先土耳其,"
    # # line_number = "200,年20,2年"
    # # line_number = "9秒90,9秒90"
    # mat_number = re.findall(r"(((\d+)秒(\d+))|(\d+(\.|-)?\d*(点|%)?))",line_number)
    # if mat_number:
    #     for temp in mat_number:
    #         print(temp[0])
    #         print(type(temp))
    # line_english = "Big Bang搜狐娱乐讯 5人偶像组合Big Bang以,搜狐房产 house.sohu.com焦点,美国电信市场研究与咨询公司DittbernerAssociates公布的,随着TD-SCDMA试商,Mozilla将推新版Firefox 挑战IE、Safari|||赛迪网讯 6月15日消息,Mozilla基金会即将发布新版Firefox"
    # mat_english = re.findall(r'(\b[a-zA-Z][a-zA-Z]+\b)',line_english)
    # if mat_english:
    #     for temp in mat_english:
    #         print(temp)
    #         print(type(temp))


    # if mat_date:
    #     for one_mat_date in mat_date.group():
    #         print(one_mat_date)
    #         line = line.replace(one_mat_date, "TAG_DATE")
    # print(line)
    # print(mat_date.group(0))
    # print("done")