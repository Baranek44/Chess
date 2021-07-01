"""
Driver file for user input and displaying the current GameState object
"""

import pygame as p
from Chess import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

"""
Initialize a global dictionary of images
"""


def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"),
                                          (SQ_SIZE, SQ_SIZE))  # Access for image 'Images['wp']


"""
Main Driver for Code, handle user input and updating the graphics
"""


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made
    # animate - Fixing bug that we can't back a move after i add a animateMove
    animate = False  # flag variable for when we should animate a move
    loadImages()  # Before the loop it will do once
    running = True
    sqSelected = ()  # if no square is selected, keep track of the last click of the user (row, col)
    playerClicks = []  # keep track of player clicks(two tuples: [(6, 4), (4, 4)]
    gameOver = False  # Checkmate = game over
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #  mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  # (x, y) location of my mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected = ()  # deselect
                        playerClicks = []  # Clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # Add for both 1st and 2nd clicks
                    if len(playerClicks) == 2:  # For a second player click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()  # reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_x:  # just reset game after click x
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawTextOnBoard(screen, 'Black wins by checkmate')
            else:
                drawTextOnBoard(screen, 'White wins by checkmate')
        elif gs.staleMate:
            gameOver = True
            drawTextOnBoard(screen, 'Draw')

        clock.tick(MAX_FPS)
        p.display.flip()


"""
Graphics within a current game state
"""


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  # Drawing squares on the board
    highLightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # Drawing pieces on the top of those squares


"""
Draw the squares and top left square is always white
"""


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]  # One square white starting on the top left
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draw the pieces on the board using GameState.board
"""


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # Not empty
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Some animations and colors
This is for Highlight square selected and moves for piece selected
"""


def highLightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():  # check if square is not empty
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # sqSelected is = piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color('red'))  # selected a color
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('brown'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


"""
Some animation etc
"""


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10  # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # here we draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # Here draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(200)


def drawTextOnBoard(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, True)
    textObject = font.render(text, 0, p.Color('Yellow'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Gray"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
