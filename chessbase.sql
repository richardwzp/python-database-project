drop database if exists chess_base;
CREATE DATABASE IF NOT EXISTS chess_base;

USE chess_base;

CREATE TABLE IF NOT EXISTS ChessPosition (
	Position VARCHAR(256) BINARY NOT NULL,
    NextTurn ENUM ("Black", "White"),
    PRIMARY KEY(Position, NextTurn)
);

CREATE TABLE IF NOT EXISTS TimeControl (
	ID INT AUTO_INCREMENT NOT NULL,
    Length INT NOT NULL,
    Increment INT NOT NULL,
    PRIMARY KEY (ID)
);

CREATE TABLE IF NOT EXISTS Player (
	Username VARCHAR(64) BINARY NOT NULL,
    ELO INT NOT NULL,
    PlayerRank VARCHAR(64) DEFAULT NULL,
    PRIMARY KEY (Username)
);

CREATE TABLE IF NOT EXISTS Game (
	GameID INT AUTO_INCREMENT NOT NULL,
    GameDate DATE NOT NULL,
    BlackPlayer VARCHAR(64) BINARY NOT NULL,
    WhitePlayer VARCHAR(64) BINARY NOT NULL,
    Winner ENUM ("Black", "White", "Draw"),
    TimeControl INT,
    PRIMARY KEY (GameID),
    FOREIGN KEY (TimeControl) REFERENCES TimeControl(ID) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (BlackPlayer) REFERENCES Player(Username) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (WhitePlayer) REFERENCES Player(Username) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS GamePositionRelationship (
	GamePosId INT AUTO_INCREMENT NOT NULL,
    MoveNumber INT NOT NULL,
    GameID INT NOT NULL,
	Position VARCHAR(256) BINARY NOT NULL,
    NextTurn ENUM ("Black", "White"),
    PRIMARY KEY (GamePosId),
    FOREIGN KEY (GameID) REFERENCES Game(GameID) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (Position, NextTurn) REFERENCES ChessPosition(Position, NextTurn) ON UPDATE RESTRICT ON DELETE RESTRICT
);

# this table contains all the openings, including the variations. we have another table
# to store the different variations of the openings.
CREATE TABLE Opening (
    Name VARCHAR(64) UNIQUE NOT NULL,
    Position VARCHAR(256) BINARY NOT NULL,
    PRIMARY KEY (Name),
    FOREIGN KEY (Position) REFERENCES ChessPosition(Position) ON UPDATE RESTRICT ON DELETE RESTRICT
);

# stores the mappings of openings to variation
CREATE TABLE OpeningVariations (
	ID INT AUTO_INCREMENT NOT NULL,
    MainLineName VARCHAR(64) NOT NULL, 
    VariationName VARCHAR(64) NOT NULL,
    PRIMARY KEY (ID),
    FOREIGN KEY (MainLineName) REFERENCES Opening(Name) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (VariationName) REFERENCES Opening(Name) ON UPDATE RESTRICT ON DELETE RESTRICT
);



-- INSERT INTO Player (Username, ELO) VALUES ("wzp", 1500);
SELECT * FROM Player;
-- DELETE FROM Player WHERE Username = "wzp";

-- INSERT INTO Game (GameDate, BlackPlayer, WhitePlayer, Winner, TimeControl) VALUES
--                   (Date("2021-04-03"), "pleaslucian", "wzprichard", "White", null);
-- insert into TimeControl (Length, Increment) Value(180, 0);

Select * FROM Game;
Select * FROM TimeControl;
SELECT * FROM GamePositionRelationship;
SELECT * FROM ChessPosition;


  INSERT INTO ChessPosition (Position, NextTurn)
  VALUES ("rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/PPP2PPP/RNBQKBNR", "White");
  INSERT INTO ChessPosition (Position, NextTurn)
  VALUES ("rnbqkbnr/pp3ppp/4p3/2ppP3/3P4/2P5/PP3PPP/RNBQKBNR", "Black");
  INSERT INTO Opening (Name, Position)
  VALUES ("French Defense", "rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/PPP2PPP/RNBQKBNR");
  INSERT INTO Opening (Name, Position)
  VALUES ("French Defense: Advance variation", "rnbqkbnr/pp3ppp/4p3/2ppP3/3P4/2P5/PP3PPP/RNBQKBNR");
  INSERT INTO OpeningVariations (MainLineName, VariationName)
  VALUES ("French Defense", "French Defense: Advance variation");
