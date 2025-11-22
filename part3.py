import pygame
import sys
import random
import time
from pygame.locals import *
import subprocess

pygame.init()
pygame.mixer.init()

try:
    move_sound = pygame.mixer.Sound("puzzlemove.mp3")
    win_sound = pygame.mixer.Sound("winsound.mp3")
except pygame.error as e:
    print(f"Error loading sound: {e}")
    move_sound = win_sound = None
    
TIME_LIMIT = 5 * 60
BASICFONT = pygame.font.Font(None, 36)
w_of_board = 5
h_of_board = 5
block_size = 75
win_width = 800
win_height = 600
FPS = 30
BLANK = None

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BGCOLOR = (0, 0, 50)
TILECOLOR = (240, 240, 240)
TEXTCOLOR = BLACK
BORDERCOLOR = (204, 204, 153)
BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE
GRAY = (150, 150, 150)
TEXT = WHITE  # Define TEXT color


XMARGIN = int((win_width - (block_size * w_of_board + (w_of_board - 1))) / 2)
YMARGIN = int((win_height - (block_size * h_of_board + (h_of_board - 1))) / 2)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

best_score = None
def update_best_score(moves):
    global best_score
    if best_score is None or moves < best_score:
        best_score = moves

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT,  RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT, HINT_SURF, HINT_RECT, NEXT_LEVEL_SURF, NEXT_LEVEL_RECT, w_of_board, h_of_board, XMARGIN, YMARGIN
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption('SLIDE N SOLVE')
    BASICFONTSIZE = 20 
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
    RESET_SURF, RESET_RECT = makeText('Reset', TEXT, BGCOLOR, BASICFONT, win_width - 150, win_height - 50)
    NEW_SURF, NEW_RECT = makeText('New Game', TEXT, BGCOLOR, BASICFONT, win_width - 150, win_height - 100)
    SOLVE_SURF, SOLVE_RECT = makeText('Auto Solve', TEXT, BGCOLOR, BASICFONT, win_width - 150, win_height - 150)
    HINT_SURF, HINT_RECT = makeText('Hint', TEXT, BGCOLOR, BASICFONT, win_width - 150, win_height - 200)

    # Initially, Next Level button is disabled (GRAY)
    NEXT_LEVEL_COLOR = GRAY
    NEXT_LEVEL_SURF, NEXT_LEVEL_RECT = makeText('Next Level', BLACK, NEXT_LEVEL_COLOR, BASICFONT, win_width - 150, win_height - 250)

    mainBoard, solutionSeq = generateNewPuzzle(80, time.time(), True)
    SOLVEDBOARD = start_playing()
    allMoves = []
    game_running = True
    completion_time = None
    start_time = time.time()

    while True:
        slideTo = None
        msg = 'Press arrow keys or click the tile to slide'

        if mainBoard == SOLVEDBOARD:
            msg = 'Congratulations! Click Next Level'
            game_running = False
            pygame.mixer.Sound.play(win_sound)
            if completion_time is None:
                completion_time = time.time() - start_time
            update_best_score(len(allMoves))

        drawBoard(mainBoard, msg, game_running, start_time, completion_time, len(allMoves), best_score)

        check_exit_req()

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])
                if (spotx, spoty) == (None, None):
                    if RESET_RECT.collidepoint(event.pos):
                        mainBoard, solutionSeq = generateNewPuzzle(80, time.time(), True)
                        allMoves = []
                        start_time = time.time()
                        completion_time = None
                        game_running = True
                        NEXT_LEVEL_COLOR = GRAY  # Disable next level button
                    elif NEW_RECT.collidepoint(event.pos):
                        mainBoard, solutionSeq = generateNewPuzzle(80, time.time(), True)
                        allMoves = []
                        start_time = time.time()
                        completion_time = None
                        game_running = True
                        NEXT_LEVEL_COLOR = GRAY  # Disable next level button
                    elif SOLVE_RECT.collidepoint(event.pos):
                        rst_animation(mainBoard, solutionSeq + allMoves, start_time, game_running)
                        allMoves = []
                        game_running = False
                    elif HINT_RECT.collidepoint(event.pos) and solutionSeq:
                        hint_move = solutionSeq[len(allMoves)] if len(allMoves) < len(solutionSeq) else None
                        if hint_move:
                            sliding_animation(mainBoard, hint_move, 'Hint!', 8, start_time, game_running)
                            take_turn(mainBoard, hint_move)
                            allMoves.append(hint_move)
                    elif NEXT_LEVEL_RECT.collidepoint(event.pos) and mainBoard == SOLVEDBOARD:
                        pygame.quit()
                        subprocess.run(["python", "part4.py"])
                        sys.exit()
                if (spotx, spoty) != (None, None):
                    blankx, blanky = getBlankPosition(mainBoard)
                    if spotx == blankx + 1 and spoty == blanky:
                        slideTo = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                        slideTo = RIGHT
                    elif spotx == blankx and spoty == blanky + 1:
                        slideTo = UP
                    elif spotx == blankx and spoty == blanky - 1:
                        slideTo = DOWN
            elif event.type == KEYUP and game_running:
                if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                    slideTo = DOWN

        if slideTo and game_running:
            pygame.mixer.Sound.play(move_sound)
            sliding_animation(mainBoard, slideTo, msg, 8, start_time, game_running)
            take_turn(mainBoard, slideTo)
            allMoves.append(slideTo)

        pygame.display.update()
        FPSCLOCK.tick(FPS)



def terminate():
    pygame.quit()
    sys.exit()

def check_exit_req():
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event)


def start_playing():
    counter = 1
    board = []
    for x in range(w_of_board):
        column = []
        for y in range(h_of_board):
            column.append(counter)
            counter += w_of_board
        board.append(column)
        counter -= w_of_board * (h_of_board - 1) + w_of_board - 1

    board[w_of_board - 1][h_of_board - 1] = BLANK
    return board


def getBlankPosition(board):
    for x in range(w_of_board):
        for y in range(h_of_board):
            if board[x][y] == BLANK:
                return (x, y)


def take_turn(board, move):
    blankx, blanky = getBlankPosition(board)

    if move == UP:
        board[blankx][blanky], board[blankx][blanky +
                                             1] = board[blankx][blanky + 1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky -
                                             1] = board[blankx][blanky - 1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx +
                                     1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx -
                                     1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]


def isValidMove(board, move):
    blankx, blanky = getBlankPosition(board)
    return (move == UP and blanky != len(board[0]) - 1) or \
           (move == DOWN and blanky != 0) or \
           (move == LEFT and blankx != len(board) - 1) or \
           (move == RIGHT and blankx != 0)


def ramdom_moves(board, lastMove=None):
    
    validMoves = [UP, DOWN, LEFT, RIGHT]

    
    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)

    return random.choice(validMoves)


def getLeftTopOfTile(block_x, block_y):
    left = XMARGIN + (block_x * block_size) + (block_x - 1)
    top = YMARGIN + (block_y * block_size) + (block_y - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    for block_x in range(len(board)):
        for block_y in range(len(board[0])):
            left, top = getLeftTopOfTile(block_x, block_y)
            tileRect = pygame.Rect(left, top, block_size, block_size)
            if tileRect.collidepoint(x, y):
                return (block_x, block_y)
    return (None, None)


def draw_block(block_x, block_y, number, adjx=0, adjy=0):
    left, top = getLeftTopOfTile(block_x, block_y)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx,
                     top + adjy, block_size, block_size))
    text_renderign = BASICFONT.render(str(number), True, TEXTCOLOR)
    text_in_rect = text_renderign.get_rect()
    text_in_rect.center = left + \
        int(block_size / 2) + adjx, top + int(block_size / 2) + adjy
    DISPLAYSURF.blit(text_renderign, text_in_rect)

def makeText(text, color, bgcolor, font, left, top):
    text_rendering = font.render(text, True, color, bgcolor)  # No error now
    text_rect = text_rendering.get_rect()
    text_rect.topleft = (left, top)
    return text_rendering, text_rect

def drawBoard(board, message, game_running, start_time, completion_time, moves=0, best_score=None):
    DISPLAYSURF.fill(BGCOLOR)
    
    # Display Moves Taken at top-right
    moves_text = BASICFONT.render(f"Moves: {moves}", True, WHITE)
    DISPLAYSURF.blit(moves_text, (win_width - 150, 20))  # <-- Move to top-right

    # Display Best Score at top-right
    if best_score is not None:
        best_text = BASICFONT.render(f"Best Score: {best_score}", True, WHITE)
        DISPLAYSURF.blit(best_text, (win_width - 150, 50))  # <-- Move to top-right
    if message:
        text_rendering, text_in_rect = makeText(message, MESSAGECOLOR, BGCOLOR, BASICFONT, 5, 5)
        DISPLAYSURF.blit(text_rendering, text_in_rect)

    timer_rendering, timer_rect = None, None

    if completion_time is not None:
        minutes = int(completion_time // 60)
        seconds = int(completion_time % 60)
        timer_text = f"Completed in: {minutes}:{seconds:02}"
    else:
        elapsed_time = int(time.time() - start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        timer_text = f"Time: {minutes:02}:{seconds:02}"
        timer_rendering, timer_rect = makeText(timer_text, WHITE, BGCOLOR, BASICFONT, 5, 40)


    if timer_rendering is not None and timer_rect is not None:
        DISPLAYSURF.blit(timer_rendering, timer_rect)


    for block_x in range(len(board)):
        for block_y in range(len(board[0])):
            if board[block_x][block_y]:
                draw_block(block_x, block_y, board[block_x][block_y])

    left, top = getLeftTopOfTile(0, 0)
    width = w_of_board * block_size
    height = h_of_board * block_size
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)
    DISPLAYSURF.blit(HINT_SURF, HINT_RECT)
    DISPLAYSURF.blit(NEXT_LEVEL_SURF, NEXT_LEVEL_RECT)
    # Now the Hint button will be displayed

    pygame.display.update()




def sliding_animation(board, direction, message, animationSpeed, start_time, game_running):
    blankx, blanky = getBlankPosition(board)
    if direction == UP:
        move_in_xaxis = blankx
        move_in_yaxis = blanky + 1
    elif direction == DOWN:
        move_in_xaxis = blankx
        move_in_yaxis = blanky - 1
    elif direction == LEFT:
        move_in_xaxis = blankx + 1
        move_in_yaxis = blanky
    elif direction == RIGHT:
        move_in_xaxis = blankx - 1
        move_in_yaxis = blanky

   
    drawBoard(board, message, game_running, start_time, None)
    baseSurf = DISPLAYSURF.copy()
  
    take_left, take_top = getLeftTopOfTile(move_in_xaxis, move_in_yaxis)
    pygame.draw.rect(baseSurf, BGCOLOR, (take_left,
                     take_top, block_size, block_size))

    for i in range(0, block_size, animationSpeed):
       
        check_exit_req()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            draw_block(move_in_xaxis, move_in_yaxis,
                       board[move_in_xaxis][move_in_yaxis], 0, -i)
        if direction == DOWN:
            draw_block(move_in_xaxis, move_in_yaxis,
                       board[move_in_xaxis][move_in_yaxis], 0, i)
        if direction == LEFT:
            draw_block(move_in_xaxis, move_in_yaxis,
                       board[move_in_xaxis][move_in_yaxis], -i, 0)
        if direction == RIGHT:
            draw_block(move_in_xaxis, move_in_yaxis,
                       board[move_in_xaxis][move_in_yaxis], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateNewPuzzle(numSlides, start_time, game_running):
    board = start_playing()
    game_running = True
    sequence = []
    board = start_playing()
    drawBoard(board,'', game_running ,start_time,None)
    pygame.display.update()
   
    pygame.time.wait(500)
    lastMove = None
    for i in range(numSlides):
        move = ramdom_moves(board, lastMove)
        sliding_animation(board, move, 'Resetting Puzzle...',
                          animationSpeed=int(block_size / 3),start_time=start_time,game_running=game_running)
        take_turn(board, move)
        sequence.append(move)
        lastMove = move
    return (board, sequence)


def rst_animation(board, allMoves,start_time,game_running):
   
    reverse_moves = allMoves[:]
    reverse_moves.reverse()

    for move in reverse_moves:
        if move == UP:
            opp_moves = DOWN
        elif move == DOWN:
            opp_moves = UP
        elif move == RIGHT:
            opp_moves = LEFT
        elif move == LEFT:
            opp_moves = RIGHT
        sliding_animation(board, opp_moves, '',
                        int(block_size / 2),start_time,game_running)
        take_turn(board, opp_moves)

        

if __name__ == '__main__':
    main()




