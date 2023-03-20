#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CREATE TABLE `other_bid_info_test` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键自增id',
  `uuid` varchar(32) NOT NULL COMMENT '根据url生成md5',
  `title` varchar(200) DEFAULT '' COMMENT '项目名称',
  `notice_type` tinyint(4) DEFAULT '1' COMMENT '公告类型,1:招标;2中标',

  `bid_type` varchar(100) DEFAULT '' COMMENT '招标类型:预招标;招标;变更公告;废标公告 ''中标类型:中标候选人;中标结果;合同;验收公告''',
  `bidding_type` varchar(100) DEFAULT '' COMMENT '招标方式,根据bid_type归纳出来的',
  `invite_company` varchar(255) DEFAULT '' COMMENT '招标公司',
  `win_company` varchar(255) DEFAULT '' COMMENT '中标公司,包含多个的话以逗号分隔',
  `agency_company` varchar(255) DEFAULT '' COMMENT '代理公司',
  `pub_province` varchar(100) DEFAULT '' COMMENT '发布所在省',
  `pub_city` varchar(100) DEFAULT '' COMMENT '发布所在市',
  `pub_district` varchar(100) DEFAULT '' COMMENT '发布所在区(备用字段)',
  `pub_addr` varchar(100) DEFAULT '' COMMENT '发布详细地址(备用字段)',
  `pub_time` varchar(100) DEFAULT '' COMMENT '发布时间',
  `tender_time` timestamp NULL DEFAULT '1971-01-01 00:00:00' COMMENT '标书获取截止时间',
  `item_number` varchar(50) DEFAULT '' COMMENT '项目编号',
  `products` varchar(200) DEFAULT '' COMMENT '产品,多个以逗号分隔',
  `money` varchar(20) DEFAULT '' COMMENT '招标金额',
  `unit` varchar(10) DEFAULT '元' COMMENT '招标金额单位',
  `notice_detail` longtext COMMENT '公告详情',
  `url` varchar(200) DEFAULT '' COMMENT '原文链接',
  `filepath` varchar(200) DEFAULT '' COMMENT '文件链接',
  `doc` varchar(200) DEFAULT '' COMMENT '附件链接',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '数据插入表格的时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '数据被更新的时间',
  `source_name` varchar(200) DEFAULT '' COMMENT '数据源网站名称',
  `other` varchar(400) DEFAULT '' COMMENT '一个备用字段，放一些能拿到，但是现在没说要要的内容',
  PRIMARY KEY (`id`),
  UNIQUE KEY `u_idx_data` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=2410936 DEFAULT CHARSET=utf8mb4 COMMENT='招投标项目基本信息';
"""
