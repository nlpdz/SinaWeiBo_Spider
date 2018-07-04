# SinaWeiBo_Spider
新浪微博爬虫（利用了代理）

## 文件说明

```
config.py -------------- 配置数据库信息，代理池，测试代理</br>
grab.py   -------------- 抓取微博信息</br>
hotsearch.py ----------- 抓取微博热搜关键词，并找相应的微博</br>
httptools.py ----------- 代理函数文件</br>
weibo_analysis.sql ----- 数据库结构文件</br>
```

## 爬虫过程
```
根据给定关键词，获取所有相关博主的信息，然后依次爬取每一个博主的所有微博。
```
