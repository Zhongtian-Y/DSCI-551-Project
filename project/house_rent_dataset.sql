/*
 Navicat MySQL Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 80016 (8.0.16)
 Source Host           : localhost:3306
 Source Schema         : usercrud

 Target Server Type    : MySQL
 Target Server Version : 80016 (8.0.16)
 File Encoding         : 65001

 Date: 01/05/2024 21:04:43
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for house_rent_dataset
-- ----------------------------
DROP TABLE IF EXISTS `house_rent_dataset`;
CREATE TABLE `house_rent_dataset`  (
  `HouseID` int(11) NULL DEFAULT NULL,
  `PostedOn` date NULL DEFAULT NULL,
  `BHK` int(11) NULL DEFAULT NULL,
  `Rent` int(11) NULL DEFAULT NULL,
  `Size` int(11) NULL DEFAULT NULL,
  `City` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `FurnishingStatus` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of house_rent_dataset
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
