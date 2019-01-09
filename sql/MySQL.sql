use deepocean;

-- drop table if exists `mad_report`;
-- drop table if exists `mad_loss`;
-- drop table if exists `mad_processedfile`;

create table `mad_report` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(255) not NULL,
    `is_malicious` bool not NULL,
    `ua` longtext not NULL,
    `url` longtext not NULL,
    `srcip` varchar(255) not NULL,
    `srcport` int not NULL,
    `dstip` varchar(255) not NULL,
    `dstport` int not NULL,
    `time` datetime(6) not NULL,
    `detected_by_cnn` bool not NULL,
    `device` varchar(255) not NULL,
    `os` varchar(255) not NULL,
    `browser` varchar(255) not NULL,
    `type` varchar(255) not NULL,
    PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

create table `mad_loss` (
    `id` int NOT NULL AUTO_INCREMENT,
    `time` datetime(6) not NULL,
    `loss` double not NULL,
    PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

create table `mad_processedfile` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(255) not NULL,
    PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

create table `mad_tobeprocessedfile` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(255) not NULL,
    `status` bool not NULL,
    PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
