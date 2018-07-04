/*
Navicat MySQL Data Transfer

Source Server         : 本地
Source Server Version : 50711
Source Host           : localhost:3306
Source Database       : weibo_analysis

Target Server Type    : MYSQL
Target Server Version : 50711
File Encoding         : 65001

Date: 2018-03-20 16:45:33
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `user_info`
-- ----------------------------
DROP TABLE IF EXISTS `user_info`;
CREATE TABLE `user_info` (
  `id` varchar(20) NOT NULL COMMENT '主键',
  `nike` varchar(40) DEFAULT 'not name' COMMENT '微博名称',
  `image_url` varchar(500) DEFAULT NULL COMMENT '头像地址',
  `home_page` varchar(500) DEFAULT NULL COMMENT '主页',
  `follow_count` int(10) DEFAULT '0' COMMENT '关注人数',
  `followers_count` int(10) DEFAULT '0' COMMENT '粉丝',
  `gender` varchar(2) DEFAULT NULL COMMENT '博主性别 m 男  |f女',
  `urank` int(3) DEFAULT '0' COMMENT '微博等级',
  `description` varchar(300) DEFAULT NULL COMMENT '微博说明',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of user_info
-- ----------------------------

-- ----------------------------
-- Table structure for `weibo_content`
-- ----------------------------
DROP TABLE IF EXISTS `weibo_content`;
CREATE TABLE `weibo_content` (
  `id` varchar(50) COLLATE utf8mb4_bin NOT NULL,
  `url` varchar(1000) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '微博详情地址',
  `date` date DEFAULT NULL COMMENT '发布日期',
  `content` text CHARACTER SET utf8mb4 COMMENT '微博内容',
  `liked_num` int(10) DEFAULT NULL COMMENT '点赞数',
  `comment_num` int(10) DEFAULT NULL COMMENT '评论数',
  `shared_num` int(10) DEFAULT NULL COMMENT '转发数',
  `userid` varchar(20) COLLATE utf8mb4_bin NOT NULL,
  `source` varchar(100) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '来源',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of weibo_content
-- ----------------------------

-- ----------------------------
-- Table structure for `work`
-- ----------------------------
DROP TABLE IF EXISTS `work`;
CREATE TABLE `work` (
  `id` int(10) NOT NULL AUTO_INCREMENT COMMENT '主键，无实际意义',
  `jobname` varchar(200) DEFAULT NULL COMMENT '任务名称',
  `job_user_id` varchar(20) DEFAULT NULL COMMENT '当前扫描用户id',
  `current_page` int(10) DEFAULT NULL COMMENT '当前扫描页数',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of work
-- ----------------------------
