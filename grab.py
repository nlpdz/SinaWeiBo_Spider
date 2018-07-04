# encoding=utf-8
''' 抓取微博信息 
    目前该文件只能根据关键词找用户，再查找用户的所有微博
    数据库相关的bug还没调好，暂时不影响使用（主键冲突的直接丢弃了）


'''

from httptools import *
from config import *
import threadpool
import time

# 根据关键字查找微博用户，返回用户id 的list


def getuser(key, page):
    url = "https://m.weibo.cn/api/container/getIndex?containerid=100103type=3&q=" + \
        key + "&t=0&page=" + str(page)
    url = urllib.parse.quote(url, safe='/:?=')
    # print(url)
    data = use_proxy(url, proxy_addr())
    cards = json.loads(data).get('data').get(
        'cards')
    if(cards == []):
        return []
    if page == 1:
        content = cards[1].get('card_group')
    else:
        content = cards[0].get('card_group')
    userlist = []
    for item in content:
        userid = item.get('user').get('id')
        userlist.append(userid)
    return userlist


# 获取微博大V账号的用户基本信息，如：微博昵称、微博地址、微博头像、关注人数、粉丝数、性别、等级等
def get_userInfo(id):
    if not os.path.exists(id):
        os.makedirs(id)
    url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + id
    data = use_proxy(url, proxy_addr())
    content = json.loads(data).get('data')
    profile_image_url = content.get('userInfo').get('profile_image_url')
    description = content.get('userInfo').get('description')
    home_page = content.get('userInfo').get('profile_url')
    verified = content.get('userInfo').get('verified')
    follow_count = content.get('userInfo').get('follow_count')
    nike = content.get('userInfo').get('screen_name')
    followers_count = content.get('userInfo').get('followers_count')
    gender = content.get('userInfo').get('gender')
    urank = content.get('userInfo').get('urank')
    print("微博昵称：" + nike + "\n" + "微博主页地址：" + home_page + "\n" + "微博头像地址：" + profile_image_url + "\n" + "是否认证：" + str(verified) + "\n" + "微博说明：" +
          description + "\n" + "关注人数：" + str(follow_count) + "\n" + "粉丝数：" + str(followers_count) + "\n" + "性别：" + gender + "\n" + "微博等级：" + str(urank) + "\n")
    try:
        saveuser(id, nike, profile_image_url, home_page, follow_count,
                 followers_count, gender, urank, description)
    except pymysql.err.IntegrityError as e:
        print(e)
    except urllib.error.HTTPError as e:
        print('url:\t' + url)
        print('proxy_ip:\t' + proxy_addr)
        print(e)
        if '403' in str(e) or '418' in str(e):
            raise e


# 获取微博主页的containerid，爬取微博内容时需要此id
def get_containerid(url):
    data = use_proxy(url, proxy_addr())
    content = json.loads(data).get('data')
    for data in content.get('tabsInfo').get('tabs'):
        if(data.get('tab_type') == 'weibo'):
            containerid = data.get('containerid')
    return containerid


# 根据用户id获取全部微博内容信息,并保存到文本中，内容包括：每条微博的内容、
# 微博详情页面地址、点赞数、评论数、转发数,来源等
def get_weibo(id, jobname):
    # if not os.path.exists(id):
    #     os.makedirs(id)
    curr_work = querywork(jobname)
    # print('job info')
    # print(curr_work)
    if curr_work is not None:
        if curr_work[2] == id:
            i = curr_work[3]
        else:
            i = 1
    else:
        i = 1
    url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + id
    containerid = get_containerid(url)

    while True:
        weibo_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + \
            id + '&containerid=' + containerid + '&page=' + str(i)
        # print('\t' + weibo_url)
        proxy_addr1 = proxy_addr()
        try:
            data = use_proxy(weibo_url, proxy_addr1)
            # print(weibo_url)
            # download_gif(data, filename)
            content = json.loads(data).get('data')
            cards = content.get('cards')
            # print(data)
            if(len(cards) > 0):
                for j in range(len(cards)):
                    print("     -----正在爬取第" + str(i) + "页，第" + str(j) +
                          "条微博------")
                    card_type = cards[j].get('card_type')
                    if(card_type == 9):
                        mblog = cards[j].get('mblog')
                        attitudes_count = mblog.get('attitudes_count')
                        comments_count = mblog.get('comments_count')
                        created_at = mblog.get('created_at')
                        if len(created_at) < 6:
                            created_at = '2018-' + created_at
                        if '前' in created_at:
                            today = datetime.date.today()
                            created_at = '%d-%d-%d' % (today.year,
                                                       today.month, today.day)
                        if '昨天' in created_at:
                            today = datetime.date.today()
                            created_at = '%d-%d-%d' % (today.year,
                                                       today.month, today.day - 1)
                        # print('日期 ' + created_at)
                        reposts_count = mblog.get('reposts_count')
                        scheme = cards[j].get('scheme')
                        text = mblog.get('text')
                        userid = mblog.get('user').get('id')
                        wid = mblog.get('id')
                        source = mblog.get('source')
                        # 微博数据存储到数据库
                        saveblog(wid, scheme, created_at, text,  int(attitudes_count),
                                 int(comments_count), int(reposts_count), userid, source)
                        savework(jobname, id, i)
                i += 1
                time.sleep(5)
            else:
                break
        except urllib.error.HTTPError as e:
            print('url:\t' + url)
            print('proxy_ip:\t' + proxy_addr1)
            print(e)
            if '403' in str(e) or '418' in str(e):
                raise e
        except Exception as e:
            print(e)
            i += 1
            pass


# 保存微博到数据库
def saveblog(wid, url, date, content,  liked_num, comment_num, shared_num, user_id, source):
    content = content.replace('\'', '\\\'')
    # 打开数据库连接
    db = pymysql.connect(host="localhost", port=3306, user=dbuser, passwd=dbpwd,
                         db="weibo_analysis", charset="utf8mb4")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    sql = """INSERT INTO weibo_content(id,url,date, content, liked_num, comment_num,shared_num,userid,source)
             VALUES ('%s','%s','%s','%s',%d,%d,%d,'%s','%s')""" % (wid, url, date, content, liked_num, comment_num, shared_num, user_id, source)
    # print(sql)
    # try:
    # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    db.commit()
    # except:
    # 如果发生错误则回滚
    # db.rollback()

    # 关闭数据库连接
    db.close()


# 保存用户信息
def saveuser(userid, nike, image_url, home_page, follow_count, followers_count, gender, urank, description):
    # 打开数据库连接
    db = pymysql.connect(host="localhost", port=3306, user=dbuser, passwd=dbpwd,
                         db="weibo_analysis", charset="utf8mb4")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    sql = """INSERT INTO user_info(id, nike, image_url, home_page, follow_count, followers_count, gender, urank, description)
             VALUES ('%s','%s','%s','%s',%d,%d,'%s',%d,'%s')""" % (userid, nike, image_url, home_page, follow_count, followers_count, gender, urank, description)
    # print(sql)
    # try:
    # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    db.commit()
    # except:
    # 如果发生错误则回滚
    # db.rollback()
    # 关闭数据库连接
    db.close()


# 保存任务进度
def savework(jobname, job_user_id, current_page):
    # 打开数据库连接
    db = pymysql.connect(host="localhost", port=3306, user=dbuser, passwd=dbpwd,
                         db="weibo_analysis", charset="utf8mb4")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    selectsql = "select * from work where jobname = '%s'" % (jobname)
    # 执行SQL语句
    cursor.execute(selectsql)
    # 获取记录列表
    result = cursor.fetchone()
    # print(result)
    if result is None:
        sql = """INSERT INTO work(jobname,job_user_id,current_page)
                    VALUES ('%s','%s',%d)""" % (jobname, job_user_id, current_page)
    else:
        sql = "update work set job_user_id = '%s',current_page='%s' where jobname='%s'" % (
            job_user_id, current_page, jobname)
    # print(sql)
    # try:
    # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    db.commit()
    # except:
    # 如果发生错误则回滚
    # db.rollback()
    # 关闭数据库连接
    db.close()


# 查询任务
def querywork(jobname):
    # 打开数据库连接
    db = pymysql.connect(host="localhost", port=3306, user=dbuser, passwd=dbpwd,
                         db="weibo_analysis", charset="utf8mb4")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    selectsql = "select * from work where jobname = '%s'" % (jobname)
    # 执行SQL语句
    cursor.execute(selectsql)
    # 获取记录列表
    result = cursor.fetchone()
    # 提交到数据库执行
    db.commit()

    db.close()
    return result


# 下载gif图片
def download_gif(data, filename):
    if not os.path.exists(os.path.join(filename, 'gifs')):
        os.makedirs(os.path.join(filename, 'gifs'))
    gifs = re.findall(
        r'https:\\/\\/[-A-Za-z0-9+&@#\\/%?=~_|!:,.;]+large+[-A-Za-z0-9+&@#\\/%?=~_|!:,.;]+gif', data)
    for gif1 in gifs:
        gif1 = gif1.replace('\/', '/')
        # print(gif1)
        gifdata = use_proxy_download(gif1, proxy_addr())
        with open(os.path.join(filename, 'gifs', uuid.uuid1().hex + '.gif'), 'wb') as f:
            f.write(gifdata)


# 多线程任务1 由betch_job1调用
def job_user_and_blog(userid, jobname):
    try:
        get_userInfo(userid)
        get_weibo(userid, jobname)
    except urllib.error.HTTPError as e:
        # print('url:\t' + url)
        # print('proxy_ip:\t' + proxy_addr)
        for times in range(5):

            print('sleep 1 min ')
            time.sleep(60)
            try:
                get_userInfo(userid)
                get_weibo(userid, jobname)
                break
            except urllib.error.HTTPError as e1:
                print(e1)
                pass


# 批处理任务 根据关键字查找用户，再搜索微博信息
# 多线程处理 停止后可自动重新从停止时开始
def betch_job1(key):
    start_time = time.time()
    pool = threadpool.ThreadPool(20)
    for i in range(10):
        users1 = getuser(key, i + 1)
        users2 = getuser(key, i + 1)
        attr_list = []
        ii = 1
        for userid in users1:
            li = []
            li.append(str(userid))
            li.append('博主所有微博_' + str(i) + '_' + str(userid))
            attr_list.append((li, None))
            ii = ii + 1
        ii = 1
        for userid in users2:
            li = []
            li.append(str(userid))
            li.append('博主所有微博_' + str(i) + '_' + str(userid))
            attr_list.append((li, None))
            ii = ii + 1
        print('key:' + key + '_，正在抓取第' + str(i + 1) + '页用户')
        print(attr_list)
        requests = threadpool.makeRequests(job_user_and_blog, attr_list)
        [pool.putRequest(req) for req in requests]
        pool.wait()

    print('%d second' % (time.time() - start_time))


if __name__ == "__main__":
    betch_job1('胡歌')
