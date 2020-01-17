/*
 Navicat MySQL Data Transfer

 Source Server         : 本地数据库
 Source Server Type    : MySQL
 Source Server Version : 80018
 Source Host           : localhost:3306
 Source Schema         : robot

 Target Server Type    : MySQL
 Target Server Version : 80018
 File Encoding         : 65001

 Date: 17/01/2020 12:28:39
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for 4kimg
-- ----------------------------
DROP TABLE IF EXISTS `4kimg`;
CREATE TABLE `4kimg`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `src` char(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `tag` char(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `src`(`src`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 17680 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for believe
-- ----------------------------
DROP TABLE IF EXISTS `believe`;
CREATE TABLE `believe`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `QQ` char(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `QQ`(`QQ`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 32 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for chat
-- ----------------------------
DROP TABLE IF EXISTS `chat`;
CREATE TABLE `chat`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `QQ` char(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `lastchat` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `theoption` char(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `temp` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `keyDelete` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `chance` int(11) NOT NULL DEFAULT 3,
  `messageid` int(11) NOT NULL,
  `lmessageid` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `QQ`(`QQ`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 26915 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ckeyword
-- ----------------------------
DROP TABLE IF EXISTS `ckeyword`;
CREATE TABLE `ckeyword`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `thekey` char(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `replay` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `weight` int(11) NOT NULL DEFAULT 50,
  `groupid` int(10) NULL DEFAULT 834659660,
  `reWeight` int(11) NOT NULL DEFAULT 70,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `thekey`(`thekey`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 667 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for img
-- ----------------------------
DROP TABLE IF EXISTS `img`;
CREATE TABLE `img`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `src` char(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `tag` char(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `src`(`src`) USING BTREE,
  UNIQUE INDEX `src_2`(`src`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 28671 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for keyword
-- ----------------------------
DROP TABLE IF EXISTS `keyword`;
CREATE TABLE `keyword`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keyword` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `replay` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of keyword
-- ----------------------------
INSERT INTO `keyword` VALUES (1, '壁纸关键词', '日历\\n动漫\\n风景\\n美女\\n游戏\\n影视\\n动态\\n唯美\\n设计\\n可爱\\n汽车\\n花卉\\n动物\\n节日\\n人物\\n美食\\n水果\\n建筑\\n体育\\n军事\\n非主流\\n其他\\n王者荣耀\\n护眼@@');
INSERT INTO `keyword` VALUES (3, '4K壁纸关键词', '风景\\n美女\\n游戏\\n动漫\\n影视\\n明星\\n汽车\\n动物\\n人物\\n美食\\n宗教\\n背景@@');

-- ----------------------------
-- Table structure for message
-- ----------------------------
DROP TABLE IF EXISTS `message`;
CREATE TABLE `message`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `QQ` int(11) NOT NULL,
  `message` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `time` datetime(0) NOT NULL,
  `groupid` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 22325 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for music
-- ----------------------------
DROP TABLE IF EXISTS `music`;
CREATE TABLE `music`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `QQ` char(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `type` char(10) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `likelist` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `list` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `QQ`(`QQ`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 57 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of music
-- ----------------------------
INSERT INTO `music` VALUES (57, '1487998424', 'qq', NULL, '{\"result\": [{\"name\": \"凉凉\", \"sginer\": \"杨宗纬 张碧晨 \", \"id\": 200380820}, {\"name\": \"凉凉 (Live)\", \"sginer\": \"张碧晨 杨宗纬 \", \"id\": 201820468}, {\"name\": \"凉凉\", \"sginer\": \"冯提莫 \", \"id\": 202030544}, {\"name\": \"凉凉 (Live)\", \"sginer\": \"张碧晨 \", \"id\": 218619429}, {\"name\": \"凉凉 (Live)\", \"sginer\": \"马来西亚胖哥 \", \"id\": 126712586}, {\"name\": \"凉凉 (《三生三世十里桃花》电视剧片尾曲)\", \"sginer\": \"莫相忘 \", \"id\": 126734480}, {\"name\": \"凉凉 (考试版)\", \"sginer\": \"洛天依 \", \"id\": 213038617}, {\"name\": \"凉凉（cover：杨宗纬、张碧晨）\", \"sginer\": \"杨优秀 \", \"id\": 126717845}, {\"name\": \"凉凉\", \"sginer\": \"网络歌手 \", \"id\": 124802310}, {\"name\": \"凉凉（减肥版）\", \"sginer\": \"网络歌手 \", \"id\": 125886842}], \"type\": \"qq\", \"singr\": \"杨宗纬 张碧晨 \", \"id\": 200380820, \"name\": \"凉凉\"}');

-- ----------------------------
-- Table structure for options
-- ----------------------------
DROP TABLE IF EXISTS `options`;
CREATE TABLE `options`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keys` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `thevalue` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of options
-- ----------------------------
INSERT INTO `options` VALUES (1, 'owner', '');

-- ----------------------------
-- Table structure for sensitiveword
-- ----------------------------
DROP TABLE IF EXISTS `sensitiveword`;
CREATE TABLE `sensitiveword`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `text` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `describetion` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `text`(`text`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2309 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
