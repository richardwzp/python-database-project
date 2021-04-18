
import pymysql as sql
from converter.pgn_data import PGNData
import csv
from math import ceil
import os
from flask import Flask, redirect, url_for, request
import json
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# given file name, convert the chess game, and store the data in mySQL
def import_pgn_to_sql(pgn_file_name):
    # logging into sql
    user = "root"
    password = ""
    with open("password", "r") as file:
        password = file.readline().strip()
    cnx = sql.connect(host="localhost", user=user, password=password,
                      db="chess_base", charset="utf8mb4",
                      cursorclass=sql.cursors.DictCursor)
    cur = cnx.cursor()

    # creating pgn data
    pgn_data = PGNData(pgn_file_name)
    pgn_data.export()

    # opening csv files
    file_name = pgn_file_name[0:-4] + "_moves.csv"
    file_info_name = pgn_file_name[0:-4] + "_game_info.csv"
    with open(file_name) as game_moves_csv:

        with open(file_info_name) as game_info_csv:
            spamreader = csv.reader(game_info_csv)
            spamreader.__next__()
            info = spamreader.__next__()
            game_date = "-".join(info[4].split("."))
            white_player_user_name = info[6]
            black_player_user_name = info[7]

            winner = info[8].split("-")
            winner = "Draw" if winner[0] == "1/2" else ("White" if winner[0] == "1" else "Black")

            white_elo = info[9]
            black_elo = info[11]
            time_control = info[20].split("+")
            time_control = [int(time_control[0]), 0] if len(time_control) <= 1 else [int(i) for i in time_control]


        # create player if not exists
        stmt_select_white_player = f'SELECT count(*) AS resultCount FROM Player WHERE Player.Username="{white_player_user_name}";'
        cur.execute(stmt_select_white_player)
        result = cur.fetchall()[0]["resultCount"]
        if not result:
            stmt_insert_white_player = f'INSERT INTO Player (Username, ELO) VALUES ("{white_player_user_name}", {white_elo});'
            cur.execute(stmt_insert_white_player)

        stmt_select_black_player = f'SELECT count(*) AS resultCount FROM Player WHERE Player.Username="{black_player_user_name}";'
        cur.execute(stmt_select_black_player)
        result = cur.fetchall()[0]["resultCount"]
        if not result:
            stmt_insert_black_player = f'INSERT INTO Player (Username, ELO) VALUES ("{black_player_user_name}", {black_elo});'
            cur.execute(stmt_insert_black_player)

        # create time control if not exists
        stmt_select_timeControl = f'SELECT ID AS id FROM TimeControl ' \
                      f'WHERE TimeControl.Length={time_control[0]} AND TimeControl.Increment={time_control[1]};'
        cur.execute(stmt_select_timeControl)
        returning_id = cur.fetchall()
        if not returning_id:
            stmt_insert_timeControl = f"insert into TimeControl (Length, Increment) Value({time_control[0]}, {time_control[1]});"
            cur.execute(stmt_insert_timeControl)
            cur.execute(stmt_select_timeControl)
            time_control_id = cur.fetchall()[0]["id"]
        else:
            time_control_id = returning_id[0]["id"]

        #game insertion
        stmt_insert_game = 'INSERT INTO Game (GameDate, BlackPlayer, WhitePlayer, Winner, TimeControl) VALUES ' + \
                      f'(Date("{game_date}"), "{black_player_user_name}", "{white_player_user_name}", "{winner}",{time_control_id});'
        cur.execute(stmt_insert_game)

    # select game id of current game
        stmt_select_game = f'SELECT GameID AS id FROM Game WHERE GameDate=Date("{game_date}") AND ' \
                           f'BlackPlayer="{black_player_user_name}" AND WhitePlayer="{white_player_user_name}" ' \
                           f'AND Winner="{winner}" AND TimeControl={time_control_id} ORDER BY GameID DESC LIMIT 1;'
        cur.execute(stmt_select_game)
        game_id = int(cur.fetchall()[0]["id"])
        spam_reader = csv.reader(game_moves_csv)
        spam_reader.__next__()
        for row in spam_reader:

            move_number = int(row[1])

            color = "White" if row[8].lower() == "black" else "Black"
            fen = row[9]

            # create position if not exists
            stmt_select_position = f'SELECT * FROM ChessPosition ' \
                                   f'WHERE Position = "{fen}" AND NextTurn = "{color}";'
            cur.execute(stmt_select_position)
            position_return = cur.fetchall()
            if not position_return:
                stmt_insert_position = f'INSERT INTO ChessPosition (Position, NextTurn) ' \
                                       f'VALUES ("{fen}", "{color}");'
                cur.execute(stmt_insert_position)
            # create gamePosition
            stmt_insert_gamePosition = f'INSERT INTO GamePositionRelationship ' \
                                       f'(MoveNumber, GameID, Position, NextTurn)' \
                                       f' VALUES ({ceil(move_number / 2)}, {game_id}, "{fen}", "{color}");'
            cur.execute(stmt_insert_gamePosition)
    cnx.commit()
    cur.close()
    cnx.close()
    os.remove(file_name)
    os.remove(file_info_name)

# connect to mySQL server
def server_connection():
    # logging into sql
    user = "root"
    password = ""
    with open("password", "r") as file:
        password = file.readline().strip()
    cnx = sql.connect(host="localhost", user=user, password=password,
                      db="chess_base", charset="utf8mb4",
                      cursorclass=sql.cursors.DictCursor)
    cur = cnx.cursor()
    return cur, cnx



@app.route('/update', methods = ['POST'])
@cross_origin()
# get complete pgn content, and update database with given chess game
def update():
    #
    recieved_data = request.json
    if type(recieved_data) is not str:
        return "not sucessful"

    convert(recieved_data)

    print(type(recieved_data), recieved_data)

    return "sucessful update!"



@app.route('/openingUpdate', methods=['get'])
@cross_origin()
# create or update a given opening
def openingUpdate():
    cur, cnx = server_connection()
    opening_name, opening_fen, opening_turn = request.args["name"], request.args["fen"], request.args["turn"]

    # add the position if it does not exist yet
    stmt_select_position = f'SELECT COUNT(*) AS positionCount FROM ChessPosition ' \
                           f'WHERE Position = "{opening_fen}" AND NextTurn = "{opening_turn}";'

    cur.execute(stmt_select_position)
    if int(cur.fetchall()[0]["openingPosition"]) == 0:
        stmt_insert = f'INSERT INTO ChessPosition (Position, NextTurn) VALUES ({opening_fen}, {opening_turn});'
        cur.execute(stmt_insert)

    stmt_select_opening = f'SELECT COUNT(*) AS openingCount FROM Opening WHERE Name = "{opening_name}"'
    cur.execute(stmt_select_opening)
    if int(cur.fetchall()[0]["openingCount"]) == 0:
        stmt_insert = f'INSERT INTO Opening (Name, Position) VALUES ({opening_name}, {opening_fen});'
        cur.execute(stmt_insert)
    else:
        stmt_update = f'UPDATE Opening ' \
                      f'SET Position="{opening_fen}" ' \
                      f'WHERE Name="{opening_name}";'
        cur.execute(stmt_update)

    cnx.commit()
    cur.close()
    cnx.close()
    return "1"

@app.route('/playerDelete', methods=['get'])
@cross_origin()
# delete a given player
def playerDelete():
    cur, cnx = server_connection()
    player_name = request.args["name"]
    stmt_delete_player = f'DELETE FROM Player WHERE Username = "{player_name}";'
    try:
        cur.execute(stmt_delete_player)
        cnx.commit()
        cur.close()
        cnx.close()
        return "1"
    except:
        cur.close()
        cnx.close()
        return "-1"

@app.route('/playerUpdate', methods = ['get'])
@cross_origin()
# update a given player
def playerUpdate():
    cur, cnx = server_connection()
    player_name, rank = request.args["name"], request.args["rank"]
    stmt_update_player = f'UPDATE Player ' \
                         f'SET PlayerRank = "{rank}" ' \
                         f'WHERE Username = "{player_name}"'
    try:
        cur.execute(stmt_update_player)
        cnx.commit()
        cur.close()
        cnx.close()
        return "1"
    except:
        cur.close()
        cnx.close()
        return "-1"

@app.route('/openingQuery', methods = ['get'])
@cross_origin()
# query the database for a fen position of given opening name
def openingQuery():
    cur, cnx = server_connection()
    openingName = request.args["opening"]
    stmt_select_opening = f'SELECT Position FROM Opening WHERE Name="{openingName}"'
    cur.execute(stmt_select_opening)
    returning_fen = cur.fetchall()
    cur.close()
    cnx.close()
    if not returning_fen:
        return ""
    return returning_fen[0]["Position"]

@app.route('/positionQuery', methods = ['get'])
@cross_origin()
# query the database for a fen position of given position name
def positionQuery():
    # [{player1, player2, player1rank(nullable), player2rank, winner, timecontrol}]
    cur, cnx = server_connection()
    fen, next_move = request.args["position"], request.args["nextMove"]

    #fen, next_move = "r1b1kb1r/pp2nppp/1qn1p3/3pP3/3P4/5N2/PP2BPPP/RNBQK2R", "White"

    stmt_select_chess_position = f'SELECT GameID FROM GamePositionRelationship ' \
                  f'WHERE Position = "{fen}" AND NextTurn = "{next_move}";'

    cur.execute(stmt_select_chess_position)
    all_game_id = [int(i["GameID"]) for i in cur.fetchall()]

    all_games = []
    for game_id in all_game_id:
        stmt_select_game = f'GameID AS id, GameDate AS date, BlackPlayer, WhitePlayer, ' \
                           f'player1.PlayerRank AS BlackPlayerRank, player2.PlayerRank AS WhitePlayerRank, ' \
                           f'Winner, Time.Length AS length, Time.increment AS increment FROM Game ' \
                           f'LEFT JOIN TimeControl AS Time ON Game.TimeControl=Time.ID ' \
                           f'LEFT JOIN Player AS player1 ON BlackPlayer=player1.Username ' \
                           f'LEFT JOIN Player AS player2 ON WhitePlayer=player2.Username ' \
                           f'WHERE GameID = {game_id};'
        cur.execute(stmt_select_game)
        all_games.append(cur.fetchall()[0])

        black_rank = all_games[-1]["BlackPlayerRank"]
        all_games[-1]["BlackPlayerRank"] = "no_rank" if not black_rank else black_rank
        white_rank = all_games[-1]["WhitePlayerRank"]
        all_games[-1]["WhitePlayerRank"] = "no_rank" if not white_rank else black_rank
        # change date to string
        all_games[-1]["date"] = str(all_games[-1]["date"])

    cur.close()
    cnx.close()
    return json.dumps(all_games)




def convert(data: str):
    with open("myfile.pgn", "w") as new_pgn:
        new_pgn.write(data)

    import_pgn_to_sql("myfile.pgn")
    os.remove("myfile.pgn")



if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=False, port=5000)
    import_pgn_to_sql("wzprichard_vs_pleaslucian_2021.04.03.pgn")
    #with open("wzprichard_vs_ivanchuk86_2021.04.11.pgn", "r") as file:
     #   content = file.read()
      #  convert(content)
    #positionQuery()
    # import_pgn_to_sql("wzprichard_vs_ivanchuk86_2021.04.11.pgn")