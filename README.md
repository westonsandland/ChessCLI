# ChessCLI

A simple command-line chess game against a minimal AI.

## Requirements

Python 3 is required. No additional packages are needed.

## Usage

Run the game from the repository root:

```bash
python3 chess_cli.py
```

Enter moves using coordinate notation, for example `e2e4`. The board will
update after each move and the AI will respond with a legal move.

Castling, en passant, promotions, checks and checkmate are handled by the
engine. The AI chooses random legal moves.
