
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
        create_players_args = [white_player_user_name, black_player_user_name, white_elo, black_elo]
        cur.callproc('create_player_with_elo', create_players_args)

        # stmt_select_white_player = f'SELECT count(*) AS resultCount FROM Player WHERE Player.Username="{white_player_user_name}";'
        # cur.execute(stmt_select_white_player)
        # result = cur.fetchall()[0]["resultCount"]
        # if not result:
        #     stmt_insert_white_player = f'INSERT INTO Player (Username, ELO) VALUES ("{white_player_user_name}", {white_elo});'
        #     cur.execute(stmt_insert_white_player)

        # stmt_select_black_player = f'SELECT count(*) AS resultCount FROM Player WHERE Player.Username="{black_player_user_name}";'
        # cur.execute(stmt_select_black_player)
        # result = cur.fetchall()[0]["resultCount"]
        # if not result:
        #     stmt_insert_black_player = f'INSERT INTO Player (Username, ELO) VALUES ("{black_player_user_name}", {black_elo});'
        #     cur.execute(stmt_insert_black_player)

        # create time control if not exists
        # create_time_params = [time_control[0], time_control[1]]
        create_time = f'SELECT create_time_control({time_control[0]}, {time_control[1]}) AS id'
        cur.execute(create_time)
        tmp = cur.fetchall()
        print(tmp)
        time_control_id = int(tmp[0]["id"])
        # stmt_select_timeControl = f'SELECT ID AS id FROM TimeControl ' \
        #               f'WHERE TimeControl.Length={time_control[0]} AND TimeControl.Increment={time_control[1]};'
        # cur.execute(stmt_select_timeControl)
        # returning_id = cur.fetchall()
        # if not returning_id:
        #     stmt_insert_timeControl = f"insert into TimeControl (Length, Increment) Value({time_control[0]}, {time_control[1]});"
        #     cur.execute(stmt_insert_timeControl)
        #     cur.execute(stmt_select_timeControl)
        #     time_control_id = cur.fetchall()[0]["id"]
        # else:
        #     time_control_id = returning_id[0]["id"]

        #game insertion
        # stmt_insert_game = 'INSERT INTO Game (GameDate, BlackPlayer, WhitePlayer, Winner, TimeControl) VALUES ' + \
        #               f'(Date("{game_date}"), "{black_player_user_name}", "{white_player_user_name}", "{winner}",{time_control_id});'
    #     cur.execute(stmt_insert_game)

    # # select game id of current game
    #     stmt_select_game = f'SELECT GameID AS id FROM Game WHERE GameDate=Date("{game_date}") AND ' \
    #                        f'BlackPlayer="{black_player_user_name}" AND WhitePlayer="{white_player_user_name}" ' \
    #                        f'AND Winner="{winner}" AND TimeControl={time_control_id} ORDER BY GameID DESC LIMIT 1;'
        
        # game insertion
        # select game id of current game
        create_game = f'SELECT create_game("{game_date}", "{black_player_user_name}", "{white_player_user_name}", "{winner}", {time_control_id}) AS id'
        cur.execute(create_game)
        game_id = int(cur.fetchall()[0]["id"])
        spam_reader = csv.reader(game_moves_csv)
        spam_reader.__next__()
        for row in spam_reader:

            move_number = int(row[1])

            color = "White" if row[8].lower() == "black" else "Black"
            fen = row[9]

            # # create position if not exists
            # stmt_select_position = f'SELECT * FROM ChessPosition ' \
            #                        f'WHERE Position = "{fen}" AND NextTurn = "{color}";'
            # cur.execute(stmt_select_position)
            # position_return = cur.fetchall()
            # if not position_return:
            #     stmt_insert_position = f'INSERT INTO ChessPosition (Position, NextTurn) ' \
            #                            f'VALUES ("{fen}", "{color}");'
            #     cur.execute(stmt_insert_position)
            # # create gamePosition
            # stmt_insert_gamePosition = f'INSERT INTO GamePositionRelationship ' \
            #                            f'(MoveNumber, GameID, Position, NextTurn)' \
            #                            f' VALUES ({ceil(move_number / 2)}, {game_id}, "{fen}", "{color}");'
            
            # create position if not exists, create gamePosition
            create_position_args = [fen, color, ceil(move_number/2), game_id]
            cur.callproc('create_position', create_position_args)
            # cur.execute(stmt_insert_gamePosition)
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
    opening_name, opening_fen, opening_turn, opening_mainline = " ".join(request.args["name"].split("_")), \
                                              request.args["fen"], request.args["turn"], \
                                                                " ".join(request.args["mainline"].split("_"))
    parent_opening_name = opening_name
    opening_name = opening_name if opening_mainline == "none" else opening_name + ": " + opening_mainline
    # add the position if it does not exist yet
    # sql defined function call
    stmt_insert_if_not = f'SELECT if_not_chess_position_then_insert("{opening_fen}", "{opening_turn}");'
    cur.execute(stmt_insert_if_not)

    # either add or update the opening
    cur.callproc("opening_add_or_update", [opening_name, opening_fen, opening_turn])

    if opening_mainline == "none":
        cnx.commit()
        cur.close()
        cnx.close()
        return "2"
    else:
        stmt_add_variation = f'SELECT add_opening_variation("{parent_opening_name}", "{opening_name}") AS openingCount;'
        cur.execute(stmt_add_variation)
        result = cur.fetchall()[0]["openingCount"]
        cnx.commit()
        cur.close()
        cnx.close()
        return "1" if result == 1 else "2"


@app.route('/playerDelete', methods=['get'])
@cross_origin()
# delete a given player
def playerDelete():
    cur, cnx = server_connection()
    player_name = request.args["name"]
    stmt_delete_player = f'SELECT if_exist_delete("{player_name}") AS deleteCount;'
    cur.execute(stmt_delete_player)
    cnx.commit()
    cur.close()
    cnx.close()
    return str(cur.fetchall()[0]["deleteCount"])



@app.route('/playerUpdate', methods = ['get'])
@cross_origin()
# update a given player
def playerUpdate():
    cur, cnx = server_connection()
    player_name, rank = request.args["name"], request.args["rank"]

    try:
        cur.callproc("update_player", [rank, player_name])
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
    openingName = " ".join(request.args["opening"].split("_"))
    cur.callproc("opening_query", [openingName])
    returning_fen = cur.fetchall()
    cur.close()
    cnx.close()
    if not returning_fen:
        return json.dumps({})
    return json.dumps(returning_fen[0])


@app.route('/positionQuery', methods = ['get'])
@cross_origin()
# query the database for a fen position of given position name
def positionQuery():
    cur, cnx = server_connection()
    fen, next_move = request.args["position"], request.args["nextMove"]

    cur.callproc("position_query", [fen, next_move])

    processed_games = cur.fetchall()

    for current_game in processed_games:
        black_rank = current_game["BlackPlayerRank"]
        current_game["BlackPlayerRank"] = "no_rank" if not black_rank else black_rank
        white_rank = current_game["WhitePlayerRank"]
        current_game["WhitePlayerRank"] = "no_rank" if not white_rank else white_rank
        # change date to string
        current_game["date"] = str(current_game["date"])
        time = f'{str(current_game["length"])} | {str(current_game["increment"])}'
        current_game["timeControl"] = time
        del current_game["length"]
        del current_game["increment"]

    cur.close()
    cnx.close()
    return json.dumps(processed_games)




def convert(data: str):
    with open("myfile.pgn", "w") as new_pgn:
        new_pgn.write(data)

    import_pgn_to_sql("myfile.pgn")
    os.remove("myfile.pgn")



if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=False, port=5000)

    #with open("wzprichard_vs_ivanchuk86_2021.04.11.pgn", "r") as file:
     #   content = file.read()
      #  convert(content)
    #positionQuery()
    #import_pgn_to_sql("wzprichard_vs_ivanchuk86_2021.04.11.pgn")