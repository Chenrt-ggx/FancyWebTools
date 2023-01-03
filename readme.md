# FancyWebTools

![license](https://img.shields.io/github/license/Chenrt-ggx/FancyWebTools)

## 登录相关

登录信息位于 `login/config.json`，每个站点共两个字段：

- `size_username` 为用户名的 base64 编码结果
- `size_password` 为用户密码的 base64 编码结果

目前支持的站点如下：

- 码云：`gitee`
- 志愿北京：`bv2008`
- 青春北京：`bjyouth`

## 互动视频解析

位于 `bilibili_interaction.py`，绘制指定互动视频的状态转移图，并解析内置变量。

## UP 主空间爬虫

位于 `bilibili_update.py`，爬取指定 UP 主一段时间内的动态，UP 主列表位于 `profile/pigeons.json`。

## 自动学习

位于 `bjyouth_study.py`，懂得都懂，验证码识别基于带带弟弟 OCR，膜一手。

## 志愿北京验证码

位于 `bv2008_code.py`，不关注公众号获取登录验证码，不过好像现在不用验证码了。

## 志愿北京证书下载

位于 `bv2008_cert.py`，下载个人志愿时长证明。

## 志愿北京时长查询

位于 `bv2008_query.py`，查询个人总志愿时长及参与的志愿活动。

## 码云创建/删除仓库

位于 `gitee_flush.py`，支持创建仓库/删除仓库，多的不说了，看代码就懂了。
