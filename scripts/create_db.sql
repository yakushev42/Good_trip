Drop table IF EXISTS roomType;
Drop table IF EXISTS hotel;
Drop table IF EXISTS voucher;
Drop table IF EXISTS contract;
Drop table IF EXISTS groups ;
Drop table IF EXISTS stay_excursion; 
Drop table IF EXISTS excursion ;
Drop table IF EXISTS stay ;
Drop table IF EXISTS city ;
Drop table IF EXISTS country ;
Drop table IF EXISTS route;
Drop table IF EXISTS users;

Create table users(
UserID Serial NOT NULL PRIMARY KEY,
NickName Varchar(32) UNIQUE NOT NULL,
pass_hash Varchar(255) NOT NULL,
role Varchar(10) NOT NULL
);
Create table contract(
  ContractID Serial NOT NULL PRIMARY KEY ,
  PayType Varchar(32) NOT NULL,
  UserID integer REFERENCES users(UserID)
);
Create table route(
Name Varchar(100) NOT NULL PRIMARY KEY,
Cost integer NOT NULL,
MaxSize integer NOT NULL,
MinSize integer NOT NULL,
BelaySize integer NOT NULL,
Duration integer NOT NULL,
Season Varchar(15) NOT NULL
);
Create table  groups(
GroupID Serial NOT NULL PRIMARY KEY,
DateStart Date NOT NULL,
Size integer NOT NULL,
NameRoute Varchar(100) NOT NULL REFERENCES route(Name)
);
Create table voucher(
Fio Varchar(100) NOT NULL,
Address Varchar(100) NOT NULL,
Phone Varchar(15) NOT NULL,
Passport Varchar(100) NOT NULL,
DateBirth Date NOT NULL,
GroupID integer NOT NULL REFERENCES Groups(GroupID),
ContractID integer NOT NULL REFERENCES contract(ContractID),
PRIMARY KEY(Passport,GroupID)
);
Create table country(
Name Varchar(30) NOT NULL PRIMARY KEY
);
Create table city(
Name Varchar(30) NOT NULL PRIMARY KEY,
Country Varchar(30) NOT NULL REFERENCES country(Name)
);

Create table stay(
Duration integer NOT NULL,
StayNum integer NOT NULL,
NameRoute Varchar(30) NOT NULL REFERENCES route(Name),
City Varchar(30) NOT NULL REFERENCES city(Name),
PRIMARY KEY(StayNum,NameRoute)
);

Create table hotel(
Name Varchar(30) NOT NULL PRIMARY KEY,
Type integer NOT NULL,
City Varchar(30) NOT NULL REFERENCES city(Name)
);
Create table roomType(
Type Varchar(30) NOT NULL,
NameHotel Varchar(30) NOT NULL  REFERENCES hotel(Name) ,
PRIMARY KEY(Type,NameHotel)
);
Create table excursion(
Name Varchar(30) NOT NULL PRIMARY KEY,
Duration integer NOT NULL
);
Create table stay_excursion(
StayNum integer NOT NULL,
NameRoute Varchar(30) NOT NULL,
ExcursionName Varchar(30) NOT NULL,
PRIMARY KEY(StayNum,NameRoute,ExcursionName),
FOREIGN KEY (ExcursionName) REFERENCES excursion(Name),
FOREIGN KEY (StayNum,NameRoute)  REFERENCES stay(StayNum,NameRoute)
);


CREATE OR REPLACE FUNCTION inc_size() RETURNS TRIGGER
 AS $inc_size$
 BEGIN
 UPDATE groups SET size= size + 1  WHERE groupID=new.groupID;
 RETURN NEW;
 END
 $inc_size$
LANGUAGE 'plpgsql';
CREATE OR REPLACE FUNCTION dec_size() RETURNS TRIGGER
 AS $inc_size$
 BEGIN
 UPDATE groups SET size= size -1  WHERE groupID=old.groupID;
 RETURN NEW;
 END
 $inc_size$
LANGUAGE 'plpgsql';


CREATE TRIGGER Trigger2
After INSERT
on  voucher
FOR EACH ROW EXECUTE PROCEDURE inc_size();

CREATE TRIGGER Trigger3
After DELETE
on  voucher
FOR EACH ROW EXECUTE PROCEDURE dec_size();