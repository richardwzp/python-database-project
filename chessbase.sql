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
    FOREIGN KEY (GameID) REFERENCES Game(GameID) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (Position, NextTurn) REFERENCES ChessPosition(Position, NextTurn) ON UPDATE RESTRICT ON DELETE RESTRICT
);

# this table contains all the openings, including the variations. we have another table
# to store the different variations of the openings.
CREATE TABLE Opening (
    Name VARCHAR(64) UNIQUE NOT NULL,
    Position VARCHAR(256) BINARY NOT NULL,
    NextTurn ENUM ("Black", "White") NOT NULL,
    PRIMARY KEY (Name),
    FOREIGN KEY (Position, NextTurn) REFERENCES ChessPosition(Position, NextTurn) ON UPDATE RESTRICT ON DELETE RESTRICT
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
-- SELECT * FROM Player;
-- DELETE FROM Player WHERE Username = "wzp";

-- INSERT INTO Game (GameDate, BlackPlayer, WhitePlayer, Winner, TimeControl) VALUES
--                   (Date("2021-04-03"), "pleaslucian", "wzprichard", "White", null);
-- insert into TimeControl (Length, Increment) Value(180, 0);

DELIMITER //

-- if the given chess position exists
DROP FUNCTION IF EXISTS if_chess_position_exists //
CREATE FUNCTION if_chess_position_exists(fen VARCHAR(256), nextTurn VARCHAR(10))
	RETURNS INT
    DETERMINISTIC
    READS SQL DATA
		BEGIN
        DECLARE ret_int INT;
        SELECT COUNT(*) INTO ret_int FROM ChessPosition
			WHERE Position = fen AND NextTurn = nextTurn;
        IF ret_int = 0 THEN
        return 0;
        ELSE
        return 1;
        END IF;
        END //
        
	-- if given chess position doesn't exist, then insert this position.
    -- return 1 for successful insert,
    -- return 0 if nothing was inserted
DROP FUNCTION IF EXISTS if_not_chess_position_then_insert //
	CREATE FUNCTION if_not_chess_position_then_insert(fen VARCHAR(256), nextTurn VARCHAR(10))
    RETURNS INT
    DETERMINISTIC
    READS SQL DATA
    MODIFIES SQL DATA
	BEGIN
    
    DECLARE ret_int INT;
    
	IF if_chess_position_exists(fen, nextTurn) = 0 THEN
    INSERT INTO ChessPosition (Position, NextTurn) VALUES (fen, nextTurn); 
    SELECT 1 INTO ret_int;
    ELSE
    SELECT 0 INTO ret_int;
    END IF;
    
   RETURN ret_int;
   
    END //

-- add the given opening if it doesn't exist,
-- update it with given fen if it does
DROP PROCEDURE IF EXISTS opening_add_or_update //
	CREATE PROCEDURE opening_add_or_update(IN opening_name VARCHAR(20),
    IN fen VARCHAR(256), IN next_turn ENUM("White", "Black"))
	BEGIN
    
    DECLARE opening_exist INT;
    SELECT COUNT(*) INTO opening_exist FROM Opening WHERE Name = opening_name;
	IF opening_exist = 0 THEN
    INSERT INTO Opening (Name, Position, NextTurn) 
                      VALUES (opening_name, fen, next_turn);
    ELSE
    UPDATE Opening SET Position=fen WHERE Name=opening_name;
    END IF;
	
   
    END //

-- add the opening variation, if it exists
-- return 1 if the variation is added,
-- return 0 if it is not
DROP FUNCTION IF EXISTS add_opening_variation //
CREATE FUNCTION add_opening_variation (parent_opening_name VARCHAR(256), variation_name VARCHAR(256))
RETURNS INT
DETERMINISTIC
READS SQL DATA
MODIFIES SQL DATA
BEGIN
DECLARE ret_int INT;

SELECT COUNT(*) INTO ret_int FROM Opening WHERE Name = parent_opening_name;
IF ret_int = 1 THEN
INSERT INTO OpeningVariations (MainLineName, VariationName) 
VALUES (parent_opening_name, variation_name);
ELSE 
RETURN ret_int;
END IF;

RETURN ret_int;

END //

-- delete this player if it exists,
-- return -1 if player doesn't exists
-- else return 1
DROP FUNCTION IF EXISTS if_exist_delete //
CREATE FUNCTION if_exist_delete(player_name VARCHAR(256))
RETURNS INT
DETERMINISTIC
READS SQL DATA
MODIFIES SQL DATA
BEGIN
DECLARE ret_int INT;
SELECT COUNT(*) INTO ret_int FROM Player WHERE Username = player_name;

IF ret_int = 0 THEN
RETURN -1;
ELSE
DELETE FROM Player WHERE Username = player_name;
RETURN 1;
END IF;

END //

-- given fen and move, give back all games information
DROP PROCEDURE IF EXISTS position_query //
CREATE PROCEDURE position_query(IN fen VARCHAR(256), IN nextMove ENUM("White", "Black"))
BEGIN
SELECT GameID AS id, GameDate AS date, BlackPlayer, WhitePlayer, 
                           player1.PlayerRank AS BlackPlayerRank, player2.PlayerRank AS WhitePlayerRank, 
                           Winner, Time.Length AS length, Time.increment AS increment FROM Game 
                           LEFT JOIN TimeControl AS Time ON Game.TimeControl=Time.ID 
                           LEFT JOIN Player AS player1 ON BlackPlayer=player1.Username 
                           LEFT JOIN Player AS player2 ON WhitePlayer=player2.Username 
                           JOIN GamePositionRelationship AS rel
                           ON rel.Position="{fen}" AND NextTurn= "{next_move}" AND Game.GameID=rel.GameID;
END //

-- query an opening of given name
DROP PROCEDURE IF EXISTS opening_query //
CREATE PROCEDURE opening_query(IN opening_name VARCHAR(256))
BEGIN
SELECT Position AS position, NextTurn AS turn FROM Opening WHERE Name=opening_name;
END //


-- update a player of given name
DROP PROCEDURE IF EXISTS update_player //
CREATE PROCEDURE update_player(IN player_rank VARCHAR(30), IN player_name VARCHAR(256)) 
BEGIN
UPDATE Player 
SET PlayerRank = player_rank 
WHERE Username = player_name AND
EXISTS (SELECT * FROM Player WHERE Username=player_name);
END //

DELIMITER ;
-- SELECT if_chess_position_exists("1", "White");
-- Select * FROM Game;
-- Select * FROM TimeControl;
-- SELECT * FROM GamePositionRelationship;
-- SELECT * FROM ChessPosition;

  INSERT INTO ChessPosition (Position, NextTurn)
  VALUES ("rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/PPP2PPP/RNBQKBNR", "White");
  INSERT INTO ChessPosition (Position, NextTurn)
  VALUES ("rnbqkbnr/pp3ppp/4p3/2ppP3/3P4/2P5/PP3PPP/RNBQKBNR", "Black");
  INSERT INTO Opening (Name, Position, NextTurn)
  VALUES ("French Defense", "rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/PPP2PPP/RNBQKBNR", "White");
  INSERT INTO Opening (Name, Position, NextTurn)
  VALUES ("French Defense: Advance variation", "rnbqkbnr/pp3ppp/4p3/2ppP3/3P4/2P5/PP3PPP/RNBQKBNR", "Black");
  INSERT INTO OpeningVariations (MainLineName, VariationName)
  VALUES ("French Defense", "French Defense: Advance variation");
  