CREATE DATABASE IF NOT EXISTS `deepocean`;

USE `deepocean`;

-- DROP TABLE IF EXISTS `mad_loss`;
-- DROP TABLE IF EXISTS `mad_report`;
-- DROP TABLE IF EXISTS `mad_processedfile`;
-- DROP TABLE IF EXISTS `mad_tobeprocessedfile`;

CREATE TABLE `mad_report` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(255) NOT NULL,
    `is_malicious` bool NOT NULL,
    `ua` longtext NOT NULL,
    `url` longtext NOT NULL,
    `srcip` varchar(255) NOT NULL,
    `srcport` int NOT NULL,
    `dstip` varchar(255) NOT NULL,
    `dstport` int NOT NULL,
    `time` datetime(6) NOT NULL,
    `detected_by_cnn` bool NOT NULL,
    `device` varchar(255) NOT NULL,
    `os` varchar(255) NOT NULL,
    `browser` varchar(255) NOT NULL,
    `type` varchar(255) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE `mad_loss` (
    `id` int NOT NULL AUTO_INCREMENT,
    `time` datetime(6) NOT NULL,
    `loss` double NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE `mad_processedfile` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(255) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE `mad_tobeprocessedfile` (
    `id` int NOT NULL AUTO_INCREMENT,
    `path` varchar(255) NOT NULL,
    `status` bool NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
