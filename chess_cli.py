# Simple CLI Chess with basic AI
# Author: Weston Sandland
# License: MIT

import random
from typing import List, Tuple, Optional

PIECES = {
    'P': '♙', 'p': '♟',
    'R': '♖', 'r': '♜',
    'N': '♘', 'n': '♞',
    'B': '♗', 'b': '♝',
    'Q': '♕', 'q': '♛',
    'K': '♔', 'k': '♚'
}

class Board:
    def __init__(self):
        self.board = [
            list('rnbqkbnr'),
            list('pppppppp'),
            list('........'),
            list('........'),
            list('........'),
            list('........'),
            list('PPPPPPPP'),
            list('RNBQKBNR')
        ]
        self.white_turn = True
        self.castling_rights = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.en_passant = None

    def display(self):
        print('  a b c d e f g h')
        for i, row in enumerate(self.board):
            print(8 - i, end=' ')
            for piece in row:
                print(PIECES.get(piece, '.'), end=' ')
            print(8 - i)
        print('  a b c d e f g h')

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < 8 and 0 <= c < 8

    def get(self, r: int, c: int) -> str:
        if self.in_bounds(r, c):
            return self.board[r][c]
        return '.'

    def set(self, r: int, c: int, val: str):
        if self.in_bounds(r, c):
            self.board[r][c] = val

    def clone(self):
        b = Board()
        b.board = [row[:] for row in self.board]
        b.white_turn = self.white_turn
        b.castling_rights = self.castling_rights.copy()
        b.en_passant = self.en_passant
        return b

    def is_white(self, piece: str) -> bool:
        return piece.isupper()

    def opposite(self, piece: str) -> str:
        return piece.swapcase()

    def king_pos(self, white: bool) -> Tuple[int, int]:
        target = 'K' if white else 'k'
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == target:
                    return r, c
        return (-1, -1)

    def moves_for_piece(self, r: int, c: int) -> List[Tuple[int, int, Optional[str]]]:
        piece = self.get(r, c)
        if piece == '.':
            return []
        dirs = []
        moves = []
        white = self.is_white(piece)
        forward = -1 if white else 1
        start_row = 6 if white else 1
        enemy = str.islower if white else str.isupper
        ally = str.isupper if white else str.islower

        if piece.upper() == 'P':
            # forward
            if self.get(r + forward, c) == '.':
                moves.append((r + forward, c, None))
                if r == start_row and self.get(r + 2 * forward, c) == '.':
                    moves.append((r + 2 * forward, c, 'e' + chr(ord('a') + c)))
            # captures
            for dc in (-1, 1):
                if enemy(self.get(r + forward, c + dc)):
                    moves.append((r + forward, c + dc, None))
            # en passant
            if self.en_passant:
                er, ec = 8 - int(self.en_passant[1]), ord(self.en_passant[0]) - ord('a')
                if r + forward == er and abs(c - ec) == 1:
                    moves.append((er, ec, 'ep'))
        elif piece.upper() == 'N':
            knight_moves = [(2, 1), (1, 2), (-1, 2), (-2, 1),
                            (-2, -1), (-1, -2), (1, -2), (2, -1)]
            for dr, dc in knight_moves:
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr, nc) and not ally(self.get(nr, nc)):
                    moves.append((nr, nc, None))
        elif piece.upper() == 'B' or piece.upper() == 'R' or piece.upper() == 'Q':
            if piece.upper() in ('B', 'Q'):
                dirs += [(1,1), (1,-1), (-1,1), (-1,-1)]
            if piece.upper() in ('R', 'Q'):
                dirs += [(1,0), (-1,0), (0,1), (0,-1)]
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while self.in_bounds(nr, nc):
                    if ally(self.get(nr, nc)):
                        break
                    moves.append((nr, nc, None))
                    if enemy(self.get(nr, nc)):
                        break
                    nr += dr
                    nc += dc
        elif piece.upper() == 'K':
            king_moves = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
            for dr, dc in king_moves:
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr, nc) and not ally(self.get(nr, nc)):
                    moves.append((nr, nc, None))
            # castling
            rights = [('K', 0, 5, 6, 7), ('Q', 0, 3, 2, 0)] if white else [('k', 7,5,6,7), ('q',7,3,2,0)]
            kr, rook_col = (7, 0) if white else (0, 0)
            for right, rrow, kf, kt, rc in rights:
                if self.castling_rights[right]:
                    if all(self.get(rrow, col) == '.' for col in range(min(kf, kt), max(kf, kt)+1)):
                        if not self.is_in_check(white) and not self.square_under_attack(rrow, kf, not white) and not self.square_under_attack(rrow, kt, not white):
                            moves.append((rrow, kt, right))
        return moves

    def all_moves(self, white: bool) -> List[Tuple[int, int, int, int, Optional[str]]]:
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.get(r, c)
                if piece != '.' and (piece.isupper() == white):
                    for nr, nc, flag in self.moves_for_piece(r, c):
                        moves.append((r, c, nr, nc, flag))
        return moves

    def square_under_attack(self, r: int, c: int, by_white: bool) -> bool:
        for sr in range(8):
            for sc in range(8):
                piece = self.get(sr, sc)
                if piece != '.' and (piece.isupper() == by_white):
                    for nr, nc, _ in self.moves_for_piece(sr, sc):
                        if nr == r and nc == c:
                            return True
        return False

    def is_in_check(self, white: bool) -> bool:
        kr, kc = self.king_pos(white)
        if kr == -1:
            return True
        return self.square_under_attack(kr, kc, not white)

    def make_move(self, r: int, c: int, nr: int, nc: int, flag: Optional[str]=None):
        piece = self.get(r, c)
        target = self.get(nr, nc)
        self.set(r, c, '.')
        self.set(nr, nc, piece)
        self.en_passant = None
        if piece.upper() == 'P' and nr in (0,7):
            self.set(nr, nc, 'Q' if piece.isupper() else 'q')
        if flag and flag.startswith('e') and len(flag)==2:
            self.en_passant = flag
        if flag == 'ep':
            self.set(r, nc, '.')
        if piece.upper() == 'K':
            self.castling_rights['K' if piece.isupper() else 'k'] = False
            self.castling_rights['Q' if piece.isupper() else 'q'] = False
            if flag in ('K','k'):
                self.set(nr,5,'R' if piece.isupper() else 'r')
                self.set(nr,7,'.')
            if flag in ('Q','q'):
                self.set(nr,3,'R' if piece.isupper() else 'r')
                self.set(nr,0,'.')
        if piece.upper() == 'R':
            if r==7 and c==0: self.castling_rights['Q']=False
            if r==7 and c==7: self.castling_rights['K']=False
            if r==0 and c==0: self.castling_rights['q']=False
            if r==0 and c==7: self.castling_rights['k']=False
        self.white_turn = not self.white_turn

    def legal_moves(self, white: bool) -> List[Tuple[int,int,int,int,Optional[str]]]:
        res = []
        for r,c,nr,nc,flag in self.all_moves(white):
            tmp = self.clone()
            tmp.make_move(r,c,nr,nc,flag)
            if not tmp.is_in_check(white):
                res.append((r,c,nr,nc,flag))
        return res

    def is_checkmate(self, white: bool) -> bool:
        return self.is_in_check(white) and not self.legal_moves(white)


def parse_move(move: str) -> Tuple[int,int,int,int]:
    move = move.replace(' ','')
    if len(move)!=4:
        raise ValueError('format must be like e2e4')
    c1 = ord(move[0])-ord('a')
    r1 = 8-int(move[1])
    c2 = ord(move[2])-ord('a')
    r2 = 8-int(move[3])
    return r1,c1,r2,c2


def ai_move(board: Board):
    moves = board.legal_moves(board.white_turn)
    if moves:
        return random.choice(moves)
    return None


def main():
    board = Board()
    while True:
        board.display()
        if board.is_checkmate(board.white_turn):
            print('Checkmate! {} wins'.format('Black' if board.white_turn else 'White'))
            break
        print("{} to move".format('White' if board.white_turn else 'Black'))
        if board.white_turn:
            move = input('Enter your move (e2e4): ').strip()
            try:
                r,c,nr,nc = parse_move(move)
            except Exception as e:
                print('Invalid format')
                continue
            legal = board.legal_moves(True)
            if (r,c,nr,nc,None) not in legal and not any(l[:4]==(r,c,nr,nc) for l in legal):
                print('Illegal move')
                continue
            for l in legal:
                if l[:4]==(r,c,nr,nc):
                    board.make_move(*l)
                    break
        else:
            move = ai_move(board)
            if not move:
                print('Stalemate!')
                break
            print('AI move: {}{}{}{}'.format(chr(move[1]+97),8-move[0],chr(move[3]+97),8-move[2]))
            board.make_move(*move)

if __name__ == '__main__':
    main()
