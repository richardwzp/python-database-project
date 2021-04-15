
import pymysql as sql
from converter.pgn_data import PGNData
import csv
from math import ceil
import os
from flask import Flask, redirect, url_for, request


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



app = Flask(__name__)
@app.route('/update', methods = ['POST'])
def update():
    #
    recieved_data = request.json
    if type(recieved_data) is not str:
        return "not sucessful"
    # convert(recieved_data)

    print(type(recieved_data), recieved_data)

    return "sucessful update!"

    #convert(data)


def convert(data: str):
    # TODO: make the pgn
    with open("myfile.pgn", "w") as new_pgn:
        new_pgn.write(data)

    import_pgn_to_sql("myfile.pgn")
    os.remove("myfile.pgn")


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=False, port=5000)
    # with open("wzprichard_vs_ivanchuk86_2021.04.11.pgn", "r") as file:
    #     content = file.read()
    #     convert(content)
