# -*- coding:utf-8 -*-
import thulac
import jieba
import re
import chardet
import sys
reload(sys)
sys.setdefaultencoding('utf8')

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
    return s1






if __name__=="__main__":
    jieba.add_word("TAG_NUMBER")
    line = "第TAG_NUMBER届奥林匹克运动会官方网站"
    line1 = "月工资TAG_NUMBER元"
    text = jieba.cut(line)

    text1 = jieba.cut(line1)
    print(" ".join(word for word in text1))
    line = "1234|||很高兴认识你234"
    mat_number = re.match(r"\d+\|\|\|",line)
    if mat_number:
        print(mat_number.group(0))

    # line3 = "2017年６月９日２０时１５分，“中星九号”广播电视直播卫星在西昌卫星发射中心成功发射。"
    # line2 = "6月24日２０时１５分下午，浙江绍兴市档案馆正在接受捐赠收藏５．１２米“心系汶川”丝绸长卷珍品。"
    # line2_ = p(line2).encode("utf-8")
    # line3_ = p(line3).encode("utf-8")
    # # print(p(line3))
    # print (line3_)
    # line4='2017年6月9日20时15分,“中星九号”广播电视直播卫星在西昌卫星发射中心成功发射。'
    # print(type(line3_))
    # print(type(line4))
    # print(type(line2_))
    # print(line2_)
    # mat_test = re.search(r"((\d{4}年)?\d{1,2}月\d{1,2}日\d{1,2}时\d{1,2}分)", line2_)
    # print(mat_test.group(0))
    # s1 = strQ2B(line3.encode())
    # print(s1)
    # mat_test = re.search(r"(([0-9０-９]{4}年)?[0-9０-９]{1,2}月[0-9０-９]{1,2}日[0-9０-９]{1,2}时[0-9０-９]{1,2}分)", s1)
    # print(mat_test.group(0))
    # line = "１．反对宪法基本原则，危害国家安全、政权稳定统一的；煽动民族仇恨、民族歧视的；"
    # line2 = "6月24日下午，浙江绍兴市档案馆正在接受捐赠收藏５．１２米“心系汶川”丝绸长卷珍品。"
    # line3 = "2017年６月９日２０时１５分，“中星九号”广播电视直播卫星在西昌卫星发射中心成功发射。"
    # print(chardet.detect(line3))
    # line_test = "5.12"
    # mat_number = re.search(r"[0-9０-９]{1,2}\.[0-9０-９]{1,2}", line_test)
    # line_test_ = "2017年6月9日20时15分"
    # print(chardet.detect(line_test_))
    # "６月 ９日 ２０时 １５分 ， “ 中星九号 ” 广播 电视 直播 卫星 在 西昌 卫星 发射 中心 成功 发射 。"
    # "搜狐 体育 讯 北京 时间 TAG_DATE 消息 勇士 主帅 老尼尔森 向 外界 宣布 ， 他 将 继续 执教 勇士 一 年 。 老尼尔森 对于 他 决定 回到 金州 一 事 显得 十分 的 轻松 ， 他 说 ： “ 我 思考 了 一 段 回到 勇士 ， 那么 他 将 有 可能 得到 一 年 TAG_NUMBER 美元 的 年薪 。"
    # line4 = "新媒邮箱满了无法收发邮件问题"
    # "新媒 邮箱 满 了 无法 收发 邮件 问题"
    # title = "老尼尔森表态续约勇士　称将在新赛季使用新战术"
    # line5 = "搜狐体育讯　北京时间６月４日消息　勇士主帅老尼尔森向外界宣布，他将继续执教勇士一年。老尼尔森对于他决定回到金州一事显得十分的轻松，他说：“我思考了一段时间，最后还是想回来，决定这件事情并不没有那么的困难，我已经做好继续战斗。如果老尼尔森回到勇士，那么他将有可能得到一年５１０万美元的年薪。而这也将是他生涯第２９次执教，而如果他在下赛季能拿下至少５３场胜利，那么他也将超过兰尼－威尔肯斯成为ＮＢＡ历史上获得胜利最多的教练。老尼尔森同时称如果只要能和球队相处的融洽，大家都开心，那么就会发挥更大的效用。目前勇士已经开始在选秀市场上猎艳，在未来三周内将继续试训新秀。勇士在本次选秀中拥有第１４和２６号签位，老尼尔森表示目前没有打算交易他们的选秀权，因为他相信今年的新秀相质量大大高于去年，而他也毫不忌讳的表示勇士将会选中一个大个子。　勇士在０７－０８赛季只取得了４８胜３４负的战绩，排在西部第九无缘季后赛，而老尼尔森不使用新人也饱受外界的非议。不过老尼尔森一改常态，称在新赛季将采用新战术思想，而且还会启用新人，像去年新秀布兰登－怀特和马科－贝里内利将都会进入轮换阵容。老尼尔森说：“在去年的时候球队的想法很简单，只是单纯的想再次进季后赛而已，不过最后没有实现。像他们这样的年轻人都是球队的未来，我已经做好了精神和身体上的准备。”（责任编辑：雷霆）"
    # line6 = "非洲本色［图６］|||大图欣赏图片名：　上传网友：　图片故事：　图片来源：四川在线相关内容"
    # mat_ = re.search(r"(\d{4}年\d{1,2}月\d{1,2}日\d{1,2}时\d{1,2}分)", line_test_)
    # # mat = re.search(r"(\d{1,2}月\d{1,2}日)",line_test)
    # mat_test = re.search(r"(([0-9０-９]{4}年)?[0-9０-９]{1,2}月[0-9０-９]{1,2}日[0-9０-９]{1,2}时[0-9０-９]{1,2}分)", line3)
    # mat_number = re.search(r"[0-9０-９]{1,2}\.[0-9０-９]{1,2}",line_test)
    # # print mat.groups()
    # # ('2016-12-12',)
    # # print mat.group(0)
    # print(mat_.group(0))
    # print(mat_number.group(0))
    # print(mat_test.group(0))
    # 2016-12-12

    # thu1 = thulac.thulac(seg_only=True)
    # text = thu1.cut(line5, text=True)
    # print(text)