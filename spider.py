# -*-coding=utf-8 #-*-
# @Time :2020/6/29 9:38
# @Author:lzz
# @File:spider.py


from bs4 import BeautifulSoup  # 网页解析，获取数据
import re  # 正则表达式，与文字匹配
import xlwt  # 制定URL，获取网页数据
import urllib.request, urllib.error  # 进行excel操作
import sqlite3  # 进行sqlite数据库操作


# 创建正则表达式
# 影片链接
findLink = re.compile(r'<a href="(.*?)">')
# 影片图片
findImaSrc = re.compile(r'<img.*src="(.*?)"', re.S)  # re.S   让换行符包含在字符中
# 影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
# 影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 找到评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
# 找到概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
# 找到影片相关内容
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)
# 找到影片年份
findyear = re.compile(r'\d{4}')
# 找到影片类型
findcountry = re.compile(r'\d{4}(.*)')


def main():
    baseurl = "https://movie.douban.com/top250?start="
    datalist = getData(baseurl)
    savepath = "豆瓣电影Top 250.xls"
    dbpath = "movie.db"
    # 保存数据
    saveData(datalist,savepath)
    # saveData2DB(datalist, dbpath)

# 爬取网页
def getData(baseurl):
    datalist = []
    for i in range(0, 10):
        url = baseurl + str(i * 25)
        html = askURL(url)  # 保存爬取的网页源码

        # 逐一解析数据
        soup = BeautifulSoup(html, "html.parser")

        for item in soup.find_all('div', class_="item"):
            # print(item)  # 测试
            data = []  # 保存
            item = str(item)

            # re库正则表达式来查找指定字符串,形成列表

            Link = re.findall(findLink, item)[0]  # 链接
            # print(Link)
            data.append(Link)

            ImaSrc = re.findall(findImaSrc, item)[0]  # 图片链接
            # print(ImaSrc)
            data.append(ImaSrc)

            Title = re.findall(findTitle, item)[0]  # 片名：可能只有一个中文名，没有外译名字
            if (len(Title) == 2):
                # print("完整title="+Title)
                cTitle = Title[0]  # 添加中文名
                # print(cTitle)
                data.append(Title)
                oTitle = Title[1].replace("/", "")  # 外译片名
                # print(oTitle)
                # data.append(' ')
            else:
                data.append(Title)
                # data.append(' ')
                # print(Title)

            Rating = re.findall(findRating, item)[0]  # 评分
            data.append(Rating)

            Judge = re.findall(findJudge, item)[0]  # 评价人数
            data.append(Judge)

            Inq = re.findall(findInq, item)  # 概述
            if len(Inq) != 0:
                Inq = Inq[0].replace("。", "")  # 去掉句号
                data.append(Inq)
            else:
                data.append(" ")  # 留空

            Bd = re.findall(findBd, item)[0]  # 相关内容

            temp = re.search('[0-9]+.*\/?', Bd).group().split('/')
            year, country, category = temp[0], temp[1], temp[2]  # 得到年份、地区、类型

            data.append(year)
            data.append(country)
            data.append(category)

            datalist.append(data)  # 把处理好的一部电影信息放入datalist

    return datalist


# 请求得到一个指定的网页内容
def askURL(url):
    head = {  # 模拟浏览器头部信息，向服务器发送消息
        "User-Agent": " Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 83.0.4103.116Safari / 537.36"
    }  # 告诉浏览器我们接受什么水平的文件内容
    request = urllib.request.Request(url, headers=head)
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


# 保存数据
def saveData(datalist, savepath):
    print("save...")
    book = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象
    sheet = book.add_sheet('豆瓣电影Top250', cell_overwrite_ok=True)  # 创建工作表

    # 制作表头
    col = ("电影详情链接", "图片链接", "中文名",  "评分", "评价数", "概述", "上映年份","制片国家","类型")
    for i in range(0, len(col)):
        sheet.write(0, i, col[i])

    for i in range(0, 250):
        # print("第%d条"%(i+1))
        data = datalist[i]
        for j in range(0, len(col)):
            sheet.write(i + 1, j, data[j])

    book.save(savepath)  # 保存


def saveData2DB(datalist, dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            # if (index == 4 or index == 5):
            #     continue
            data[index] = '"' + data[index] + '"'
        sql = '''
                insert into movie250(
                info_link, pic_link, cname, score,rated, introduction,year_release,country,category )
                values(%s)''' % ",".join(data)
        # print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close


def init_db(dbpath):
    sql = '''
        create table movie250
        (
        id integer primary key autoincrement,
        info_link text,
        pic_link text,
        cname varchar,
        score numeric,
        rated numeric,
        introduction text,
        year_release numeric ,
        country varchar ,
        category varchar
        )
    '''
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # 调用函数
    main()
    # print("爬取完毕！")
    # init_db("movietest.db")