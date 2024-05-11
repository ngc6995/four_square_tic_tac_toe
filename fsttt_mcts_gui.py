# fsttt_mcts_gui.py

'''
Four Square Tic Tac Toe

Instead of working with a 3x3 grid, you have a 4x4.
You are still using two players; X and O. Play is
like regular tic tac toe except that players can win
three ways:

4 corners, 4 in a square (anywhere on the board) or
4 in a row (vertical, horizontal, diagonal).
'''

import tkinter as tk
import customtkinter as ctk
from itertools import product
from mcts.searcher.mcts import MCTS
from fsttt_mcts_state import FSTicTacToeState


ctk.set_appearance_mode("dark") # Modes: system (default), light, dark
ctk.set_default_color_theme("green") # Themes: blue (default), dark-blue, green


class Constants:
    PLAY_FIRST = 1
    PLAY_SECOND = 2
    FG_COLOR = "DarkSlateGray"
    X_COLOR = "DarkOrange"
    O_COLOR = "Olive"


class FSTicTacToe(ctk.CTk, Constants): 
    def __init__(self):
        super().__init__()

        self.title("Four Square Tic Tac Toe")
        self.resizable(False, False)

        self.font1 = ctk.CTkFont(family="Arial", size=50)
        self.font2 = ctk.CTkFont(family="Arial", size=15)

        self.choice = ctk.IntVar(master=self, value=1)
        self.time_limit = ctk.StringVar(master=self, value="1000")
        
        button_index = -1
        self.btn_square = []
        self.btn_index = [[row, col] for row in range(3, -1, -1) for col in range(0, 4)]
        
        for row, col in product(range(4), range(4)):
            button_index += 1
            self.btn_square.append(ctk.CTkButton(master=self,
                                                 height=70, width=70,
                                                 font=self.font1,
                                                 fg_color=self.FG_COLOR,
                                                 text="",
                                                 hover=False,
                                                 command=lambda i=button_index:self.player_move(i)))  
            self.btn_square[button_index].grid(row=row, column=col, padx=5, pady=5)

        self.rdb_play_first = ctk.CTkRadioButton(master=self, font=self.font2, text="Play first", variable=self.choice, value=1)
        self.rdb_play_first.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.rdb_play_second = ctk.CTkRadioButton(master=self, font=self.font2, text="Play second", variable=self.choice, value=2)
        self.rdb_play_second.grid(row=4, column=2, columnspan=2, pady=10)
               
        ctk.CTkLabel(master=self, font=self.font2, text="Search time limit (ms)").grid(row=5, column=0, columnspan=2)
                
        self.ent_time_limit = ctk.CTkEntry(master=self, font=self.font2, textvariable=self.time_limit)
        self.ent_time_limit.grid(row=5, column=2, columnspan=2)
        
        self.lbl_message = ctk.CTkLabel(master=self, font=self.font2, text="Powered by MCTS")
        self.lbl_message.grid(row=6, column=0, columnspan=2)      
        
        self.btn_play = ctk.CTkButton(master=self, font=self.font2, text="Play", command=self.lets_play) 
        self.btn_play.grid(row=6, column=2, columnspan=2, pady=10)
 
    def gui_setup(self, action):
        if action == "ready":
            rdb_play_first_state = "normal"
            rdb_play_second_state = "normal"
            ent_time_limit_state = "normal"
            btn_play_state = "normal"           
        elif action == "play":
            rdb_play_first_state = "disabled"
            rdb_play_second_state = "disabled"
            ent_time_limit_state = "disabled"
            btn_play_state = "disabled"
            
            for button in self.btn_square:
                button.configure(fg_color=self.FG_COLOR, text="")
            
            if self.choice.get() == self.PLAY_FIRST:
                self.lbl_message.configure(text="Your move")
            elif self.choice.get() == self.PLAY_SECOND:
                self.lbl_message.configure(text="")
            
            if not self.time_limit.get().isnumeric() or int(self.time_limit.get()) < 1000:
                self.time_limit.set("1000")
               
        self.rdb_play_first.configure(state=rdb_play_first_state)
        self.rdb_play_second.configure(state=rdb_play_second_state)
        
        self.ent_time_limit.configure(state=ent_time_limit_state)
        self.btn_play.configure(state=btn_play_state)
        #self.update()
    
    def lets_play(self):
        self.gui_setup("play")
        self.mcts = MCTS(time_limit=int(self.time_limit.get()))
        
        if self.choice.get() == self.PLAY_FIRST:
            self.game_state = FSTicTacToeState(-1)
            self.player_mark, self.ai_mark = "X", "O"
            self.player_color, self.ai_color = self.X_COLOR, self.O_COLOR
        elif self.choice.get() == self.PLAY_SECOND:
            self.game_state = FSTicTacToeState(1)
            self.player_mark, self.ai_mark = "O", "X"
            self.player_color, self.ai_color = self.O_COLOR, self.X_COLOR
            self.ai_move()

    def player_move(self, index):
        if self.btn_play.cget("state") == "disabled":
            row, col = self.btn_index[index]
        
            if self.game_state.board[row][col] == 0:
                self.game_state.board[row][col] = self.game_state.current_player
                self.game_state.current_player *= -1
                #print(self.game_state)
                self.btn_square[index].configure(fg_color=self.player_color, text=self.player_mark)         
                self.lbl_message.configure(text="")
                self.update()

                if self.game_state.is_terminal():
                    self.game_over()
                else:
                    self.ai_move()
                    if self.game_state.is_terminal():
                        self.game_over()
                    else:
                        self.lbl_message.configure(text="Your move")

    def ai_move(self):
        move = self.mcts.search(self.game_state)
        self.game_state.board[move.row][move.col] = self.game_state.current_player
        self.game_state.current_player *= -1
        #print(self.game_state)
        index = self.btn_index.index([move.row, move.col])
        self.btn_square[index].configure(fg_color=self.ai_color, text=self.ai_mark)

    def game_over(self):
        reward = self.game_state.get_reward()
        
        if reward == 1:
            self.lbl_message.configure(text="I win!")
        elif reward == -1:
            self.lbl_message.configure(text="You win!")
        else:
            self.lbl_message.configure(text="It's a draw!")

        self.gui_setup("ready")

if __name__ == "__main__":
    app = FSTicTacToe()
    app.mainloop()
