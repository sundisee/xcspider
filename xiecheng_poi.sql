/*
 Navicat Premium Data Transfer

 Source Server         : mafengwo
 Source Server Type    : MySQL
 Source Server Version : 50163
 Source Host           : localhost
 Source Database       : mafengwo

 Target Server Type    : MySQL
 Target Server Version : 50163
 File Encoding         : utf-8

 Date: 01/03/2014 18:41:33 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `xiecheng_poi`
-- ----------------------------
DROP TABLE IF EXISTS `xiecheng_poi`;
CREATE TABLE `xiecheng_poi` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prov_name` varchar(255) NOT NULL DEFAULT '',
  `prov_url` varchar(255) NOT NULL DEFAULT '',
  `city_name` char(50) NOT NULL DEFAULT '',
  `city_url` varchar(255) NOT NULL DEFAULT '',
  `city_rank` int(11) NOT NULL,
  `poi_name` varchar(255) NOT NULL DEFAULT '',
  `poi_url` varchar(255) NOT NULL DEFAULT '',
  `poi_type` varchar(255) NOT NULL DEFAULT '',
  `poi_rank` int(11) NOT NULL,
  `star_rank` varchar(255) NOT NULL DEFAULT '',
  `is_province` int(11) NOT NULL,
  `poi_tags` varchar(255) NOT NULL DEFAULT '',
  `poi_play_time` varchar(255) NOT NULL DEFAULT '',
  `poi_tel` varchar(255) NOT NULL DEFAULT '',
  `poi_open_time` varchar(255) NOT NULL DEFAULT '',
  `poi_ticket` varchar(255) NOT NULL DEFAULT '',
  `poi_addr` varchar(255) NOT NULL DEFAULT '',
  `poi_traffic` text NOT NULL,
  `poi_desc` text NOT NULL,
  `poi_percentage` varchar(255) NOT NULL DEFAULT '',
  `poi_lat` varchar(255) NOT NULL DEFAULT '',
  `poi_lng` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

