import execjs
import requests
import json
import re
import jieba
import wordcloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def get_music_content(idcode,switch):
    """
    获取当前音乐的标题信息
    :param idcode:
    """
    if switch==1:
        typea = "playlist"
    if switch==2:
        typea = "song"
    url = f"https://music.163.com/{typea}?id={idcode}"
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'referer': 'https://music.163.com/'
    }

    resp = requests.get(url,headers=headers).text

    title = re.search(r'<title>(?P<title>.*?)</title>',resp,re.S).group("title")
    print(title)


def get_playlist_formparams(idcode, pagesize,page,cursor=-1):
    """
    通过逆向分析获取加密前表单中要传的参数，
    过程省略，这里直接将加密前的参数放在这个函数里，通过execjs模块得到加密后的参数
    :return: params、encseckey，cuosor
    """

    # 定义参数
    # offset:页面偏移量;limit最大值为100
    data =f'{{"rid":"A_PL_0_{idcode}","threadId":"A_PL_0_{idcode}","pageNo":{page},"pageSize":{pagesize},"cursor":{cursor},"offset":"0","orderType":"1","csrf_token":""}}'
    param_2 = '010001'
    param_3 = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    param_4 = '0CoJUm6Qyw8W8jud'

    # 用execjs模块读取js文件
    with open('wangyiyun.js',encoding='utf-8') as f:
        js_encrypt = f.read()
    # 固定模式对加密数据进行解密
    ctx_encrypt = execjs.compile(js_encrypt).call("d", data,param_2,param_3,param_4)

    params = ctx_encrypt["encText"]
    encseckey = ctx_encrypt["encSecKey"]
    return params, encseckey,cursor


def get_song_formparams(idcode, pagesize,page,cursor=-1):
    """
    通过逆向分析获取加密前表单中要传的参数，
    过程省略，这里直接将加密前的参数放在这个函数里，通过execjs模块得到加密后的参数
    :return: params、encseckey，cuosor
    """

    # 定义参数
    # offset:页面偏移量;limit最大值为100
    data =f'{{"rid":"R_SO_4_{idcode}","threadId":"R_SO_4_{idcode}","pageNo":{page},"pageSize":{pagesize},"cursor":{cursor},"offset":"0","orderType":"1","csrf_token":""}}'
    param_2 = '010001'
    param_3 = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    param_4 = '0CoJUm6Qyw8W8jud'

    # 用execjs模块读取js文件
    with open('wangyiyun.js',encoding='utf-8') as f:
        js_encrypt = f.read()
    # 固定模式对加密数据进行解密
    ctx_encrypt = execjs.compile(js_encrypt).call("d", data,param_2,param_3,param_4)

    params = ctx_encrypt["encText"]
    encseckey = ctx_encrypt["encSecKey"]
    return params, encseckey,cursor


def get_comment(idcode,pagesize,page,switch,cursor=-1):
    """
    获取评论信息。结合浏览器开发者工具的预览一栏（Preview）
    :return:
    """
    # 定义一个空列表，用于存放评论内容
    global comments_list
    comments_list = []

    url = "https://music.163.com/weapi/comment/resource/comments/get?csrf_token="
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'referer': f'https://music.163.com/{switch}?id={idcode}',
    }

    # 获取这个表单值不能用下面注释的方法，因为下面的方法其实是一前一后进行了两次不同的加密操作所生成的值，所以不可取，必须同一次加密所得的值才有效。
    # 判断是获取歌单数据还是获取歌曲数据
    if switch==1:
        params, encseckey,cursor = get_playlist_formparams(idcode, pagesize,page,cursor)  # 元组解包
    if switch==2:
        params, encseckey,cursor = get_song_formparams(idcode, pagesize,page,cursor)  # 元组解包
    form_datas = {
        'params': params,
        'encSecKey': encseckey
    }
    #
    # form_datas = {
    #     'params': get_formparams()[0],
    #     'encSecKey': get_formparams()[1]
    # }

    # print(form_datas)
    resp = requests.post(url,headers=headers,data=form_datas).text
    # print(resp)
    resp_dict = json.loads(resp)    # 将字典型字符串转化为字典
    # print(resp_dict)

    # 获取cursor
    cursor = resp_dict["data"]['cursor']

    print("-"*130)
    try:
        print("下面是普通评论：")
        comments = resp_dict["data"]["comments"]
        # print(comments)
        for i in comments:
            content = i["content"]
            time = i["timeStr"]
            avatarurl = i["user"]["avatarUrl"]
            nickname = i['user']['nickname']
            print("nickname:",nickname)
            print("avatarUrl(头像)",avatarurl)
            print("time（发布时间）:",time)
            print("content:",content)
            print()

            # 向列表中加入评论内容
            comments_list.append(content)

    except:
        print(f"第{page}页没有comments（普通评论）")

    print("-"*130)
    hotcomments = resp_dict["data"]["hotComments"]
    try:
        print("下面是热点评论：")
        for j in hotcomments:
            hot_content = j["content"]
            hot_time = j["timeStr"]
            hot_avatarurl = j["user"]["avatarUrl"]
            hot_nickname = j['user']['nickname']
            print("hot_nickname:",hot_nickname)
            print("hot_avatarUrl(头像)",hot_avatarurl)
            print("hot_time（发布时间）:",hot_time)
            print("hot_content:",hot_content)
            print()

            # 向列表中加入热点评论内容
            comments_list.append(hot_content)

    except:
        print(f"第{page}页没有hotcomments（热点评论）")

    return cursor


def get_pages_comment(idcode,pagesize,page,switch):
    """
    获取多页的评论信息
    :param idcode:
    :param pagesize:
    :param page:
    """
    for i in range(1, 1 + page):
        if i == 1:
            cursor = get_comment(idcode, pagesize, i, switch)
            print("获取到评论的第1页了")
            # print(cursor)
        else:
            cursor = get_comment(idcode, pagesize, i, switch, cursor)
            print(f"获取到评论的第{i}页了")


def write_txtfile(content):
    with open(r"wangyiyun_comment.txt",mode="a") as f:
        f.write(content)
    pass


def generate_wordcloud(comments_list):
    # 设置背景图片
    mask = np.array(Image.open("picture.png"))

    # 设置中文字体类型，到自己电脑 C:\Windows\Fonts 路径下“随便”找
    font = r'C:\Windows\Fonts\simsun.ttc'

    # 对传入的字符串列表进行分词，并去除中文停止词
    comment_str = " ".join(comments_list)
    result = jieba.lcut(comment_str)    # 精简模式，返回一个列表类型的结果
    with open(r"stopword.txt","r",encoding="utf-8") as f:
        allwords = f.readlines()
    stopwords = [word.strip() for word in allwords]
    result_fin = []                      # 定义一个列表，用于存储去除中文停止词后的词语
    for i in result:
        if i not in stopwords:
            result_fin.append(i)
    result_fin = " ".join(result_fin)   # 列表转化为字符串类型

    # Python：wordcloud构建词云出现关键字重复的情况添加该参数collocations=False
    wc = wordcloud.WordCloud(font_path=font,mask=mask,background_color="white",contour_color = 'steelblue',collocations=False)
    wc.generate(result_fin)            # generate（）里面的对象要求是一个字符串类型的数据
    wc.to_file(r"wordcloud.png")       # 将生成的词云图片保存到本地
    print("词云图片已保存到本地")
    # 这下面的操作是将图片在当前页面展示出来，可以不要
    # plt.imshow(wc)
    # plt.axis("off")
    # plt.show()


def main(idcode,pagesize,page,switch):
    get_music_content(idcode,switch)
    get_pages_comment(idcode,pagesize,page,switch)


if __name__ == '__main__':
    # 用户输入音乐id等等
    print("请问你要获取什么类型的评论，是歌单还是歌曲？")
    switch = int(input("歌单请输入1,歌曲请输入2："))
    if switch ==1:
        idcode = int(input("请输入歌单（playlist）的id（如2201957752 、 346089）："))
        pagesize = str(input("请输入一次读取评论的条数（最大输入1000）："))
        page = int(input("请输入你要爬取评论的页数："))
        # 执行主函数
        main(idcode,pagesize,page,switch)
        generate_wordcloud(comments_list)
        print()
        print("数据采集完成")
    if switch==2:
        idcode = int(input("请输入歌曲（song）的id（如2201957752）："))
        pagesize = str(input("请输入一次读取评论的条数（最大输入1000）："))
        page = int(input("请输入你要爬取评论的页数："))
        # 执行主函数
        main(idcode, pagesize, page,switch)
        generate_wordcloud(comments_list)
        print()
        print("数据采集完成")



# 这是上面get_formparams(idcode, pagesize,page,cursor=-1)函数中发送网络请求需带的参数的介绍
"""
“rid”:“R_SO_4_1817702136” 后面这个数字是网页url后面的id (根据id变换)
“threadId”:“R_SO_4_1817702136” 同上 （根据id 变换)
“pageNo”:“2” 页码数 （变量）
“pageSize”:“20” 每一页评论的数量 常量
“cursor”:“1613900247044” 应该是时间戳13位 (变量)
“offset”:“40” 偏移量 (页码数 * 20) (变量)
“orderType”:“1” 估计是啥类型是个常量
“csrf_token”:“d4339865ec133c9a7d77a25389bc0265”} 同样是个常量
    comment_str = " ".join(comments_list)

"""
