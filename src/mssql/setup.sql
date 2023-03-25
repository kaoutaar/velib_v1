
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'jcdeco') CREATE DATABASE jcdeco
GO
USE jcdeco

IF NOT EXISTS (select * from sys.tables where name=N'stations' and type='U')
    create table stations(
		city varchar(20),
        number int,
        name varchar(10),
        address varchar(100),
        latitude float,
        longitude float,
		primary key (city, number));

GO

IF NOT EXISTS (select * from sys.tables where name=N'bikes' and type='U')
    create table bikes(
		id int NOT NULL IDENTITY,
        date Datetime,
        contract_name varchar(20),
        number int,
        hour int,
        bike_stands int,
        mean_available_bikes int,
        mean_available_stands int,
		primary key (id),
		foreign key (contract_name, number) references stations (city, number));
GO


Declare @JSON varchar(max)
SELECT @JSON=BulkColumn
FROM OPENROWSET (BULK '/code/data/bruxelles.json', SINGLE_CLOB) as import

INSERT INTO stations
select 'bruxelles' as city,* from (
SELECT * FROM OPENJSON (@JSON)
WITH  (
    number int,
    name varchar(10),
    address varchar(100),
    latitude float,
    longitude float)
	) as t1


SELECT @JSON=BulkColumn
FROM OPENROWSET (BULK '/code/data/namur.json', SINGLE_CLOB) as import

INSERT INTO stations

select 'namur' as city,* from (
SELECT * FROM OPENJSON (@JSON)
WITH  (
    number int,
    name varchar(10),
    address varchar(100),
    latitude float,
    longitude float)
	) as t2

GO