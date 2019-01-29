CREATE TABLE "speedtest" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "ping" FLOAT, "dl_speed" FLOAT, "up_speed" FLOAT, "date" TEXT, "time" TEXT, "timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP, "ping_unit" INTEGER, "dl_unit" INTEGER, "up_unit" INTEGER);
CREATE TABLE "unit" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "name" TEXT NOT NULL  UNIQUE );
CREATE VIEW `group_date_min_view` AS select min(ping), min(dl_speed), min(up_speed), date from speedtest group by date order by date;
CREATE VIEW `group_date_view` AS select ping, dl_speed, up_speed, date from speedtest group by date order by date;
CREATE VIEW `max_group_date_view` AS select max(ping), max(dl_speed), max(up_speed), date from speedtest group by date order by date;
