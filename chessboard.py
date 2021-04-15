#
# import functools
# #name = input()
#
#
#
# class ChessBoard():
#     def __init__(self):
#         self.board = []
#         for i in range(8):
#             self.board += [["*" for i in range(8)]]
#         self.board[0] = ["R", "N", "B", "Q", "K", "B", "N", "R"]
#         self.board[7] = [i.lower() for i in self.board[0]]
#         self.board[1] = ["P" for _ in range(8)]
#         self.board[6] = ["p" for _ in range(8)]
#
#     def movePiece(self, move, turn):
#         if move == "0-0":
#             #TODO:
#             x = 1
#         elif move == "0-0-0":
#             #TODO:
#             x = 1
#
#         elif move[0].islower():
#             if "=" in move:
#                 #TODO: pawn promotion
#                 x = 1
#             #TODO: pawn move
#             x = 1
#
#
#
#     def possibleKnightSquare(self, sqr, color):
#         row, col = sqr
#         allPos = []
#         knight = "N" if color == "w" else "n";
#
#         allPos.append((row + 1, col + 2))
#         allPos.append((row - 1, col + 2))
#         allPos.append((row + 1, col - 2))
#         allPos.append((row - 1, col - 2))
#
#         allPos.append((row + 2, col + 1))
#         allPos.append((row - 2, col - 1))
#         allPos.append((row + 2, col - 1))
#         allPos.append((row - 2, col + 1))
#         allPos = [i for i in filter(lambda i: 8 > i[0] >= 0 and 8 > i[1] >= 0 and self.board[i][j] == knight, allPos)]
#         return allPos
#
#     def travel_until_piece(self, inc1, inc2, end1, end2, allPos, piece, row, col):
#         for i, j in zip(range(row + inc1, inc1, end1), range(col + inc2, inc2, end2)):
#             if self.board[i][j] == piece:
#                 allPos.append((i, j))
#                 break
#             elif self.board[i][j] != "*":
#                 break
#
#     def correctBishop(self, sqr, color):
#         row, col = sqr;
#         allPos = []
#         bishop = "B" if color == "w" else "b";
#
#         self.travel_until_piece(-1, -1, -1, -1, allPos, bishop, row, col)
#         self.travel_until_piece(-1, 1, -1, 8, allPos, bishop, row, col)
#         self.travel_until_piece(1, 1, 8, 8, allPos, bishop, row, col)
#         self.travel_until_piece(1, -1, 8, -1, allPos, bishop, row, col)
#
#         return allPos
#
#     def correct_rook(self, sqr, color):
#         row, col = sqr;
#         rook = "R" if color == "w" else "r"
#         allPos = []
#         self.travel_until_piece(-1, 0, -1, -1, allPos, rook, row, col)
#
#
#     def possible_Piece(self, piece, square):
#         """ return the square(s) of the piece that can reach this one"""
#         squares = []
#
#         if piece == "R":
#             x = 1
#         elif piece == "N":
#             x = 1
#
#         elif piece == "B":
#
#
#         elif piece == "Q":
#             x = 1
#         elif piece == "K":
#             x = 1
#         elif piece == "P":
#             x = 1
#



#obj = ChessBoard()
#print(obj.board)
