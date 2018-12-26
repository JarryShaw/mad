drop table if exists `mad_reports`;

create table `mad_reports` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` text not NULL,
    `is_malicious` bool not NULL,
    `ua` text not NULL,
    `url` text not NULL,
    `srcip` text not NULL,
    `srcport` int not NULL,
    `dstip` text not NULL,
    `dstport` int not NULL,
    `time` timestamp not NULL,
    `detected_by_cnn` bool not NULL,
    `device` text not NULL,
    `os` text not NULL,
    `browser` text not NULL,
    `type` text not NULL,
    PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
