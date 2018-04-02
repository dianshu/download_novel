# download_novel
下载小说
脚本从'http://www.80txt.com/'网站下载小说。可以自定义三个参数。
. category_url 小说目录url
. headers 爬虫的请求头
. process_num 并发的进程数

最终爬取的小说保存为脚本所在目录'%d.txt' % process_num中
