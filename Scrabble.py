import time
import random
random.seed()

import copy

import numpy as np
import colorsys

import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk, ImageDraw, ImageFont
import tkinter.simpledialog

n_spaces = 15
tiles = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P',\
         'Q','R','S','T','U','V','W','X','Y','Z','?']
values = [1,  3,  3,  2,  1,  4,  2,  4,  1,  8,  5,  1,  3,  1,  1,  3,\
          10, 1,  1,  1,  3,  4,  4,  8,  4,  10, 0]

print("************************")
print("* Welcome to Scrabble! *")
print("************************")

root = Tk()

def Get_Dictionary():
    with open('Dictionary.txt', 'r') as f:
        complete_dictionary = f.read().split('\n')
        return [word.split('\t')[0] for word in complete_dictionary]

def Get_Definitions():
    with open('Dictionary.txt', 'r') as f:
        complete_dictionary = f.read().split('\n')
        return [word.split('\t')[1] for word in complete_dictionary]

def Create_Tile_Image(tile, blank=False):
    partial_tile_image = Image.open("Images/Blank.jpg")
    value = str(values[tiles.index(tile.upper())])

    text = ImageDraw.Draw(partial_tile_image)
    tile_font = ImageFont.truetype('Images/times-new-roman.ttf',180)
    value_font = ImageFont.truetype('Images/times-new-roman.ttf',50)
    tile_w, tile_h = text.textsize(tile, font=tile_font)
    value_w, value_h = text.textsize(value, font=value_font)

    if not blank:
        text.text((int((partial_tile_image.size[0]-tile_w)/2),\
               int((partial_tile_image.size[1]-1.25*tile_h)/2)),\
              tile, (0,0,0), tile_font)
        text.text((int((partial_tile_image.size[0]+5*value_w)/2),\
                   int((partial_tile_image.size[1]+1.5*1.25*value_h)/2)),\
                  value, (0,0,0), value_font)
    else:
        text.text((int((partial_tile_image.size[0]-tile_w)/2),\
               int((partial_tile_image.size[1]-1.25*tile_h)/2)),\
              tile, (220,20,60), tile_font)
        
    tile_image = Image.new("RGB", (int(partial_tile_image.size[0]*1.04),\
                                   int(partial_tile_image.size[1]*1.04)))
    tile_image.paste(partial_tile_image, (int((tile_image.size[0]-partial_tile_image.size[0])/2),\
                                         int((tile_image.size[1]-partial_tile_image.size[1])/2)))

    tile_resize_scale = 0.14
    tile_image.thumbnail((tile_resize_scale*tile_image.size[0],\
                          tile_resize_scale*tile_image.size[1]))
    
    return tile_image

def Replace_Blanks(word_string):
    QMs = ''
    if '|' in word_string:
            QMs = word_string.split('|')[1].upper()
    word_string = word_string.split('|')[0].upper()
    for i in range(len(QMs)):
        word_string = word_string.replace('?',QMs[i],1)
    return word_string

class Tile():
    def __init__(self, letter, idxs=None, blank=False):
        if letter != '':
            self.is_blank = blank
            self.image_state = Create_Tile_Image(letter, blank)
            
            self.idxs = idxs
            
            self.letter = letter.upper()
            
            if not blank:
                self.value = values[tiles.index(self.letter)]
            else:
                self.value = 0

    def copy(self):
        return Tile(self.letter, self.idxs, self.is_blank)

class Space():
        def __init__(self, tile, space_type):
            self.tile = tile
            self.space_type = space_type

            self.is_empty = True
            
            self.tile_multiplier = 1
            self.word_multiplier = 1
            read_multiplier = 1
            if 'Triple' in space_type:
                read_multiplier = 3
            elif 'Double' in space_type:
                read_multiplier = 2
            if 'Letter' in space_type:
                self.tile_multiplier = read_multiplier
            elif 'Word':
                self.word_multiplier = read_multiplier

        def Change(self, tile):
            self.tile = tile
            self.is_empty = False

class Scrabble_Board():
    def __init__(self):
        #Create a tkinter canvas
        self.canvas = Canvas(root, width=1000, height=1000)
        self.canvas.pack()

        ### Improve this? ###
        #Define canvas observational information
        N_edge = 47; E_edge = 825;
        S_edge = 709; W_edge = 220;
        
        space_width = (E_edge - W_edge)/n_spaces
        space_height = (S_edge - N_edge)/n_spaces
        
        #Define plotting observational information
        x_initial = 102; y_initial = 54;
        x_factor = 40.2; y_factor = 44;

        #Create canvas centers
        self.centers = [[(int(W_edge + (2 * j + 1) * space_width/2),\
                          int(N_edge + (2 * i + 1) * space_height/2)) for j in range(n_spaces)] for i in range(n_spaces)]

        #Create plotting centers
        self.plotting_centers = [[(int(x_initial + j * x_factor),\
                                   int(y_initial + i * y_factor)) for j in range(n_spaces)] for i in range(n_spaces)]
        
        ### Improve this? ###
        #Assign unique tiles
        self.state = [[Space(Tile(''),'') for j in range(n_spaces)] for i in range(n_spaces)]
        self.state[0][0] = Space(Tile(''),'Triple Word')
        self.state[7][0] = Space(Tile(''),'Triple Word')
        self.state[14][0] = Space(Tile(''),'Triple Word')
        self.state[0][7] = Space(Tile(''),'Triple Word')
        self.state[7][7] = Space(Tile(''),'Triple Word')
        self.state[14][7] = Space(Tile(''),'Triple Word')
        self.state[0][14] = Space(Tile(''),'Triple Word')
        self.state[7][14] = Space(Tile(''),'Triple Word')
        self.state[14][14] = Space(Tile(''),'Triple Word')
        self.state[1][1] = Space(Tile(''),'Double Word')
        self.state[13][1] = Space(Tile(''),'Double Word')
        self.state[2][2] = Space(Tile(''),'Double Word')
        self.state[12][2] = Space(Tile(''),'Double Word')
        self.state[3][3] = Space(Tile(''),'Double Word')
        self.state[11][3] = Space(Tile(''),'Double Word')
        self.state[4][4] = Space(Tile(''),'Double Word')
        self.state[10][4] = Space(Tile(''),'Double Word')
        self.state[7][7] = Space(Tile(''),'Double Word')
        self.state[4][10] = Space(Tile(''),'Double Word')
        self.state[10][10] = Space(Tile(''),'Double Word')
        self.state[3][11] = Space(Tile(''),'Double Word')
        self.state[11][11] = Space(Tile(''),'Double Word')
        self.state[2][12] = Space(Tile(''),'Double Word')
        self.state[12][12] = Space(Tile(''),'Double Word')
        self.state[1][13] = Space(Tile(''),'Double Word')
        self.state[13][13] = Space(Tile(''),'Double Word')
        self.state[5][1] = Space(Tile(''),'Triple Letter')
        self.state[9][1] = Space(Tile(''),'Triple Letter')
        self.state[1][5] = Space(Tile(''),'Triple Letter')
        self.state[5][5] = Space(Tile(''),'Triple Letter')
        self.state[9][5] = Space(Tile(''),'Triple Letter')
        self.state[13][5] = Space(Tile(''),'Triple Letter')
        self.state[1][9] = Space(Tile(''),'Triple Letter')
        self.state[5][9] = Space(Tile(''),'Triple Letter')
        self.state[9][9] = Space(Tile(''),'Triple Letter')
        self.state[13][9] = Space(Tile(''),'Triple Letter')
        self.state[5][13] = Space(Tile(''),'Triple Letter')
        self.state[9][13] = Space(Tile(''),'Triple Letter')
        self.state[3][0] = Space(Tile(''),'Double Letter')
        self.state[11][0] = Space(Tile(''),'Double Letter')
        self.state[6][2] = Space(Tile(''),'Double Letter')
        self.state[8][2] = Space(Tile(''),'Double Letter')
        self.state[0][3] = Space(Tile(''),'Double Letter')
        self.state[7][3] = Space(Tile(''),'Double Letter')
        self.state[14][3] = Space(Tile(''),'Double Letter')
        self.state[2][6] = Space(Tile(''),'Double Letter')
        self.state[6][6] = Space(Tile(''),'Double Letter')
        self.state[8][6] = Space(Tile(''),'Double Letter')
        self.state[12][6] = Space(Tile(''),'Double Letter')
        self.state[3][7] = Space(Tile(''),'Double Letter')
        self.state[11][7] = Space(Tile(''),'Double Letter')
        self.state[12][8] = Space(Tile(''),'Double Letter')
        self.state[8][8] = Space(Tile(''),'Double Letter')
        self.state[6][8] = Space(Tile(''),'Double Letter')
        self.state[2][8] = Space(Tile(''),'Double Letter')
        self.state[14][11] = Space(Tile(''),'Double Letter')
        self.state[7][11] = Space(Tile(''),'Double Letter')
        self.state[0][11] = Space(Tile(''),'Double Letter')
        self.state[8][12] = Space(Tile(''),'Double Letter')
        self.state[6][12] = Space(Tile(''),'Double Letter')
        self.state[11][14] = Space(Tile(''),'Double Letter')
        self.state[3][14] = Space(Tile(''),'Double Letter')

        self.bag_of_tiles = ['A','A','A','A','A','A','A','A','A',\
                             'B','B',\
                             'C','C',\
                             'D','D','D','D',\
                             'E','E','E','E','E','E','E','E','E','E','E','E',\
                             'F','F',\
                             'G','G','G',\
                             'H','H',\
                             'I','I','I','I','I','I','I','I','I',\
                             'J',\
                             'K',\
                             'L','L','L','L',\
                             'M','M',\
                             'N','N','N','N','N','N',\
                             'O','O','O','O','O','O','O','O',\
                             'P','P',\
                             'Q',\
                             'R','R','R','R','R','R',\
                             'S','S','S','S',\
                             'T','T','T','T','T','T',\
                             'U','U','U','U',\
                             'V','V',\
                             'W','W',\
                             'X',\
                             'Y','Y',\
                             'Z',\
                             '?','?']

        #Get the dictionary
        self.dictionary = Get_Dictionary()
        self.definitions = Get_Definitions()
        
        #Add the players
        self.canvas.create_text(200,770,fill="darkblue",font="Times 20 italic bold",
                                text="Your Score:")
        self.human_score = self.canvas.create_text(276,770,fill="darkblue",font="Times 20 italic bold",\
                                                    text="0")
        self.canvas.create_text(220,800,fill="darkblue",font="Times 20 italic bold",
                                text="Computer Score:")
        self.computer_score = self.canvas.create_text(318,800,fill="darkblue",font="Times 20 italic bold",\
                                                      text="0")
        
        #Add the Scrabble board image
        board_image = Image.open("Images/Board.jpg")
        resize_scale = 0.54
        board_image.thumbnail((resize_scale * board_image.size[0],\
                               resize_scale * board_image.size[1])) #resize image
        self.board_image_state = board_image
        
        board_img = ImageTk.PhotoImage(board_image)
        self.board_image = board_img

        rack_image = Image.open("Images/Rack.png")
        rack_image.thumbnail((400,200)) #resize image
        self.rack_image_state = rack_image
        
        rack_img = ImageTk.PhotoImage(rack_image)
        self.rack_image = rack_img
        
        self.canvas_board_image = self.canvas.create_image(500, 374, image=board_img)
        self.canvas_rack_image = self.canvas.create_image(650, 790, image=rack_img)

        self.previous_board_image_state = self.board_image_state
        self.previous_rack_image_state = self.rack_image_state

        #Words played
        self.number_of_words = 0

        #Potential Points
        self.potential_points = self.canvas.create_text(60,120,fill="darkblue",font="Times 20 italic bold",\
                                                        text="")

    def n_tiles(self):
            return len(self.bag_of_tiles)

    def Back_Up_Image(self):
        self.previous_board_image_state = self.board_image_state.copy()
        self.previous_rack_image_state = self.rack_image_state.copy()

    def Reset_Image_with_Back_Up(self):
        self.board_image_state = self.previous_board_image_state.copy()
        self.rack_image_state = self.previous_rack_image_state.copy()

        self.Update_Image()
        
    def Update_Image(self):
        board_img = ImageTk.PhotoImage(self.board_image_state)
        self.board_image = board_img

        rack_img = ImageTk.PhotoImage(self.rack_image_state)
        self.rack_image = rack_img
        
        self.canvas.itemconfigure(self.canvas_board_image, image=board_img)
        self.canvas.itemconfigure(self.canvas_rack_image, image=rack_img)

    def Update_Scores(self, human_score, computer_score):
        self.canvas.itemconfig(self.human_score, text=str(human_score))
        self.canvas.itemconfig(self.computer_score, text=str(computer_score))

    def Update_Potential_Points(self, points, hide=False):
        if not hide:
            self.canvas.itemconfig(self.potential_points, text=f"Points: {points}")
        else:
            self.canvas.itemconfig(self.potential_points, text=f"")

class Word():
    def __init__(self, word_string, first_idxs, direction):
        QMs = ''
        if '|' in word_string:
            QMs = word_string.split('|')[1].upper()
        blank_idxs = [pos for pos, char in enumerate(word_string) if char == '?']

        self.QMs = QMs
        self.word_string = word_string.split('|')[0]
        
        self.first_idxs = first_idxs
        self.direction = direction
        
        self.tiles = []
        for i in range(len(list(self.word_string))):
            if i in blank_idxs:
                tile = Tile(list(Replace_Blanks(word_string))[i], None, blank=True)
            else:
                tile = Tile(list(self.word_string)[i], None)
            if direction == "right":
                tile.idxs = (first_idxs[0], first_idxs[1] + i)
            else:
                tile.idxs = (first_idxs[0] + i, first_idxs[1])
            self.tiles.append(tile)
            
        new_tiles = []
        for tile in self.tiles:
            if board.state[tile.idxs[0]][tile.idxs[1]].is_empty:
                new_tiles.append(tile)
        self.new_tiles = new_tiles

        value = 0
        word_multiplier = 1
        for tile in self.tiles:
            if board.state[tile.idxs[0]][tile.idxs[1]].is_empty:
                value += tile.value * board.state[tile.idxs[0]][tile.idxs[1]].tile_multiplier
                word_multiplier *= board.state[tile.idxs[0]][tile.idxs[1]].word_multiplier
            else:
                value += tile.value
        value *= word_multiplier
        if len(new_tiles) == 7:
            value += 50
        self.value = value

    def copy(self):
        return Word(self.word_string, self.first_idxs, self.direction)
        
class Player():
    def __init__(self):
        self.score = 0
        self.tiles = self.pick_tiles(7)

        self.played_words = []
        self.n_played_words = len(self.played_words)

    def update_n_played_words(self):
        self.n_played_words = len(self.played_words)

    def show_tiles(self, used_tiles=[]):
        used_tile_letters = []
        for tile in used_tiles:
            if not tile.is_blank:
                used_tile_letters.append(tile.letter)
            else:
                used_tile_letters.append('?')
        for i in range(len(self.tiles)):
            tile = self.tiles[i].copy()
            if tile.letter in used_tile_letters:
                hue = Image.new('RGBA', tile.image_state.size, 'white')
                tile.image_state = Image.blend(tile.image_state.convert('RGBA'), hue, 0.5)
                used_tile_letters.remove(tile.letter)
            
            x_coordinate = 10 + 58*i
            y_coordinate = 20
            board.rack_image_state.paste(tile.image_state, (x_coordinate, y_coordinate))
            board.Update_Image()

    def pick_tiles(self, n_new_tiles):
        tiles = []
        for i in range(n_new_tiles):
            random_idx = random.randrange(board.n_tiles())
            tile_letter = board.bag_of_tiles[random_idx]
            board.bag_of_tiles.pop(random_idx)
            if tile_letter != '?':
                tiles.append(Tile(tile_letter))
            else:
                tiles.append(Tile(tile_letter, blank=True))
        return tiles

    def refresh_tiles(self, input_word):
        for tile in input_word.new_tiles:
            current_letters = [tile.letter for tile in self.tiles]
            if not tile.is_blank:
                self.tiles.pop(current_letters.index(tile.letter))
            else:
                self.tiles.pop(current_letters.index('?'))
        self.tiles += self.pick_tiles(len(input_word.new_tiles))

def Calculate_Points(created_words):
    points = 0
    for word in created_words:
        points += word.value
    return points

def Check_if_Tiles_in_Player_Tiles(input_tiles):
    player_letters = [tile.letter for tile in human.tiles]
    for tile in input_tiles:
        if not tile.is_blank:
            if tile.letter not in player_letters:
                return False
            player_letters.remove(tile.letter)
        else:
            if '?' not in player_letters:
                return False
            player_letters.remove('?')
    return True

def Get_Created_Words(input_word):
    created_words = []
    input_word_string = ''
    for tile in input_word.tiles:
        if not '|' in input_word_string:
            insert_idx = len(input_word_string)
        else:
            insert_idx = input_word_string.index('|')
        if board.state[tile.idxs[0]][tile.idxs[1]].is_empty:
            if not tile.is_blank:
                input_word_string = input_word_string[:insert_idx] + tile.letter + input_word_string[insert_idx:]
            else:
                input_word_string = input_word_string[:insert_idx] + '?' + input_word_string[insert_idx:]
                if not '|' in input_word_string:
                    input_word_string += f'|{tile.letter}'
                else:
                    input_word_string += f'{tile.letter}'
        else:
            if not board.state[tile.idxs[0]][tile.idxs[1]].tile.is_blank:
                input_word_string = input_word_string[:insert_idx] + tile.letter + input_word_string[insert_idx:]
            else:
                input_word_string = input_word_string[:insert_idx] + '?' + input_word_string[insert_idx:]
                if not '|' in input_word_string:
                    input_word_string += f'|{tile.letter}'
                else:
                    input_word_string += f'{tile.letter}'
    created_words.append(Word(input_word_string, input_word.first_idxs, input_word.direction))
    
    QMs = ''
    for tile in input_word.new_tiles:
        if input_word.direction == "right":
            i_idxs = [-1, 1]
            if tile.idxs[0] == 0:
                i_idxs = [1]
            elif tile.idxs[0] == n_spaces - 1:
                i_idxs = [-1]
            for i in i_idxs:
                if not board.state[tile.idxs[0] + i][tile.idxs[1]].is_empty:
                    created_word = ''
                    idx_iter_start = 0; idx_iter_stop = 0;
                    while not board.state[tile.idxs[0] - (1 + idx_iter_start)][tile.idxs[1]].is_empty:
                        idx_iter_start += 1
                    while not board.state[tile.idxs[0] + (1 + idx_iter_stop)][tile.idxs[1]].is_empty:
                        idx_iter_stop += 1
                    for idx in range(-idx_iter_start, idx_iter_stop + 1): 
                        if idx == 0:
                            if not tile.is_blank:
                                created_word += tile.letter
                            else:
                                created_word += '?'
                                QMs += tile.letter
                        else:
                            if not tile.is_blank:
                                created_word += board.state[tile.idxs[0] + idx][tile.idxs[1]].tile.letter
                            else:
                                created_word += '?'
                                QMs += board.state[tile.idxs[0] + idx][tile.idxs[1]].tile.letter
                    created_word += '|{QMs}'
                    created_words.append(Word(created_word,\
                                              (tile.idxs[0] - idx_iter_start, tile.idxs[1]), direction="down"))
                    break
        else:
            j_idxs = [-1, 1]
            if tile.idxs[1] == 0:
                j_idxs = [1]
            elif tile.idxs[1] == n_spaces - 1:
                j_idxs = [-1]
            for j in j_idxs:
                if not board.state[tile.idxs[0]][tile.idxs[1] + j].is_empty:
                    created_word = ''
                    idx_iter_start = 0; idx_iter_stop = 0;
                    while not board.state[tile.idxs[0]][tile.idxs[1] - (1 + idx_iter_start)].is_empty:
                        idx_iter_start += 1
                    while not board.state[tile.idxs[0]][tile.idxs[1] + (1 + idx_iter_stop)].is_empty:
                        idx_iter_stop += 1
                    for idx in range(-idx_iter_start, idx_iter_stop + 1):
                        if idx == 0:
                            if not tile.is_blank:
                                created_word += tile.letter
                            else:
                                created_word += '?'
                                QMs += tile.letter
                        else:
                            if not tile.is_blank:
                                created_word += board.state[tile.idxs[0]][tile.idxs[1] + idx].tile.letter
                            else:
                                created_word += '?'
                                QMs += board.state[tile.idxs[0]][tile.idxs[1] + idx].tile.letter
                    created_word += f'|{QMs}'
                    created_words.append(Word(created_word,\
                                              (tile.idxs[0], tile.idxs[1] - idx_iter_start), direction="right"))
                    break

    return created_words

def Check_Board_Validity(word_string, first_idxs, direction):
    if direction == "right":
        tile_idxs = [(first_idxs[0], first_idxs[1] + i) for i in range(len(word_string))]
    else:
        tile_idxs = [(first_idxs[0] + i, first_idxs[1]) for i in range(len(word_string))]

    return all(elem in [(i,j) for i in range(n_spaces) for j in range(n_spaces)] for elem in tile_idxs)

def Check_Validity(input_word, created_words):
    validity = False
    used_spaces = [tile.idxs for tile in input_word.tiles]
    
    if not Check_if_Tiles_in_Player_Tiles([tile for tile in input_word.new_tiles]):
        return False
    if board.number_of_words == 0:
        if (7,7) not in used_spaces:
            return False
        else:
            return True
    else:
        created_word_strings = [Replace_Blanks(f'{word.word_string}|word.QMs') for word in created_words]
        if not all(elem in board.dictionary for elem in created_word_strings):
            return False
        intersects_correctly = False
        if len(input_word.new_tiles) != len(input_word.tiles):
            for tile in input_word.tiles:
                if not board.state[tile.idxs[0]][tile.idxs[1]].is_empty:
                    intersects_correctly = intersects_correctly or tile.letter == board.state[tile.idxs[0]][tile.idxs[1]].tile.letter
        touches = len(created_words) > 1
        if not (intersects_correctly or touches):
            return False
         
    return True
            
def Lock_Word(input_word, player, points):
    Place_Ghost_Word(input_word.word_string + '|' + input_word.QMs, input_word.first_idxs, input_word.direction, player, Locked = True)
    board.canvas.unbind("<Button 1>")
    root.unbind("<Right>")
    root.unbind("<Down>")
    root.unbind("<Return>")

    print(f"Locking word for {points} points.\nPress \"Confirm\" to finish your turn.")
    confirm_button["state"] = "normal"

    player.played_words.append((input_word, points))
    
def Place_Ghost_Word(word_string, first_idxs, direction, player, Locked = False):
    board.Reset_Image_with_Back_Up()

    if not Check_Board_Validity(word_string.split('|'), first_idxs, direction):
        print("Your word will not fit on the board at that position. Please pick another.")
        return

    input_word = Word(word_string, first_idxs, direction)
    
    created_words = Get_Created_Words(input_word)
        
    validity = True
    if not Locked:
        validity = Check_Validity(input_word, created_words)
        
    tiles = []
    if not validity:
        for tile in input_word.tiles:
            if board.state[tile.idxs[0]][tile.idxs[1]].is_empty:
                copy_of_tile = tile.copy()
                hue = Image.new('RGBA', copy_of_tile.image_state.size, 'red')
                copy_of_tile.image_state = Image.blend(copy_of_tile.image_state.convert('RGBA'), hue, 0.5)
                tiles.append(copy_of_tile)
            else:
                if not board.state[tile.idxs[0]][tile.idxs[1]].tile.is_blank:
                    copy_of_tile = tile.copy()
                    hue = Image.new('RGBA', copy_of_tile.image_state.size, 'red')
                    copy_of_tile.image_state = Image.blend(copy_of_tile.image_state.convert('RGBA'), hue, 0.5)
                    tiles.append(copy_of_tile)
                else:
                    copy_of_tile = Tile(tile.letter, tile.idxs, blank=True)
                    hue = Image.new('RGBA', copy_of_tile.image_state.size, 'red')
                    copy_of_tile.image_state = Image.blend(copy_of_tile.image_state.convert('RGBA'), hue, 0.5)
                    tiles.append(copy_of_tile)
    else:
        for tile in input_word.tiles:
            if board.state[tile.idxs[0]][tile.idxs[1]].is_empty:
                copy_of_tile = tile.copy()
                if not Locked:
                    hue = Image.new('RGBA', copy_of_tile.image_state.size, (147,235,148))
                    copy_of_tile.image_state = Image.blend(copy_of_tile.image_state.convert('RGBA'), hue, 0.5)
                tiles.append(copy_of_tile)
            else:
                if not board.state[tile.idxs[0]][tile.idxs[1]].tile.is_blank:
                    copy_of_tile = tile.copy()
                    if not Locked:
                        hue = Image.new('RGBA', copy_of_tile.image_state.size, (147,235,148))
                        copy_of_tile.image_state = Image.blend(copy_of_tile.image_state.convert('RGBA'), hue, 0.5)
                    tiles.append(copy_of_tile)
                else:
                    copy_of_tile = Tile(tile.letter, tile.idxs, blank=True)
                    if not Locked:
                        hue = Image.new('RGBA', copy_of_tile.image_state.size, (147,235,148))
                        copy_of_tile.image_state = Image.blend(copy_of_tile.image_state.convert('RGBA'), hue, 0.5)
                    tiles.append(copy_of_tile)
            
    for tile in tiles:
        board.board_image_state.paste(tile.image_state,\
                                      board.plotting_centers[tile.idxs[0]][tile.idxs[1]])

    human.show_tiles(input_word.new_tiles)
    
    if validity:
        points = Calculate_Points(created_words)
        board.Update_Potential_Points(points)
        root.bind("<Return>",\
                  lambda event, input_word=input_word, player=player:\
                  Lock_Word(input_word, player, points))
    else:
        board.Update_Potential_Points(0, hide=True)
        root.unbind("<Return>")
    
def Get_Details_for_Word(event, word_string, player):
    def Convert_Click_to_Plot_Center(point):
        def Radial_Distance(point_A, point_B):
            return np.sqrt((point_A[0] - point_B[0])**2 + (point_A[1] - point_B[1])**2)
        
        dr = Radial_Distance(board.centers[0][0], point)
        idxs = (0,0)
        for i in range(n_spaces):
            for j in range(n_spaces):
                current_dr = Radial_Distance(board.centers[i][j], point)
                if current_dr < dr:
                    dr = current_dr
                    idxs = (i, j)
        return idxs

    click_idxs = Convert_Click_to_Plot_Center((event.x, event.y))

    Place_Ghost_Word(word_string, click_idxs, "right", player)
    root.bind("<Right>",\
              lambda event, word_string=word_string, click_idxs=click_idxs, direction="right", player=player:\
              Place_Ghost_Word(word_string, click_idxs, direction, player))
    root.bind("<Down>",\
              lambda event, word_string=word_string, click_idxs=click_idxs, direction="down", player=player:\
              Place_Ghost_Word(word_string, click_idxs, direction, player))
    
def Get_Word(player):
    word_string_validity = False
    while not word_string_validity:
        word_string = input("What word would you like to play?\n")
        word_string += '|'

        replacement_strings = ['1st','2nd']
        for i in range(word_string.count('?')):
            if word_string.count('?') == 1:
                word_string += input("What tile would you like your blank tile to represent? ")
            else:
                word_string += input("What tile would you like your {replacement_strings[i]} blank tile to represent? ")

        word_string_validity = Replace_Blanks(word_string) in board.dictionary
        if not word_string_validity:
            print("Your word is not in the offical Scrabble dictionary.")
    reset_button["state"] = "normal"
    
    board.Back_Up_Image()
    print("Where would you like to play this word?\nClick where you would like the first tile to be.\n"+\
          "You may then press <Right> or <Down> to choose a direction, and <Enter> to lock in your word.")
    board.canvas.bind("<Button 1>",\
                      lambda event, word=word_string: Get_Details_for_Word(event, word_string, player))

    confirm_button.wait_variable(word_confirmed)

def Finish_Turn(player):
    board.Update_Potential_Points(0, hide=True)
    
    for tile in player.played_words[-1][0].tiles:
        board.state[tile.idxs[0]][tile.idxs[1]].Change(tile)
        
    board.number_of_words += 1
    player.score += player.played_words[-1][1]
    player.update_n_played_words()
    player.refresh_tiles(player.played_words[-1][0])
    
def Reset_Word(player):
    word_confirmed.set(1)
    board.Reset_Image_with_Back_Up()

    if player.n_played_words != len(player.played_words):
        player.played_words.pop(-1)
    
    board.canvas.unbind("<Button 1>")
    root.unbind("<Right>")
    root.unbind("<Down>")
    root.unbind("<Return>")
    Get_Word(human)
    
board = Scrabble_Board()
human = Player()
computer = Player()

human.tiles.pop(-1)
human.tiles.append(Tile('?',blank=True))

while board.n_tiles() > 0:
    human.show_tiles()
    board.Update_Scores(human.score, computer.score)

    print(f"Number of Remaining Tiles: {board.n_tiles()}")

    word_confirmed = tk.IntVar()
    reset_button = tk.Button(root, text="Reset Word", command=lambda: Reset_Word(human))
    reset_button.place(relx=.062, rely=.05, anchor="c")
    reset_button["state"] = "disabled"
    confirm_button = tk.Button(root, text="Confirm Word", command=lambda: word_confirmed.set(1))
    confirm_button.place(relx=.062, rely=.1, anchor="c")
    confirm_button["state"] = "disabled"
    
    Get_Word(human)
    Finish_Turn(human)
    
    reset_button.place_forget()
    confirm_button.place_forget()
    
    print("\nNext Turn Commencing!\n")

root.mainloop()
