# Muto

项目取名为哥斯拉--怪兽之王里的长腿怪兽👾

![muto](https://github.com/qi20172017/Muto/blob/product/muto.jpeg)

----------------

一个支持分布式的爬虫项目

技术栈：python, java, android, js, celery，rabbitmq, mysql, psql, sqlalchemy

### 项目简介

Muto是一个支持分布式的爬虫项目，目前是写了两个APP平台的数据接口。

项目启停用systemd控制，相关代码在doc目录下。本项目采用celery+rabbitmq的框架，将每个接口的爬虫注册成一个个worker的形式。相关配置代码在app目录下。数据库支持mysql、psql，用sqlalchemy构建ORM。redis用作了缓存一点页数数据。相关代码在model目录中。最后，爬虫文件在plantform目录下。

### 部署

#### 配置文件

moen-haozu.service   根据自己实际情况配置哈，只需要改这两项就行

```shell
EnvironmentFile=/etc/conf.d/moen-haozu.conf      .conf文件的路径
WorkingDirectory=/alidata/server/Muto          ./项目路径     
```

