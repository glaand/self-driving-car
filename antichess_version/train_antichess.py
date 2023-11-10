from collections import deque
import random
import chess
import chess.variant
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.layers import Dense, Conv2D, Flatten, Input
from tensorflow.compat.v1.keras.optimizers import Adam
from tensorflow.keras.callbacks import TensorBoard
from IPython.display import display, HTML
import chess.svg
import matplotlib.pyplot as plt
from tqdm import tqdm
from config import state_space_size, action_space_size, exploration_prob, learning_rate, discount_factor
from board_function import board_to_input_array, state_to_index, move_to_output_array,  count_pieces_by_color, normalize_input
from Q_funct import update_q_table, choose_action, calculate_reward
# Chess Variant Antichess











# Neural Network Model alpha zero
input_layer = Input(shape=state_space_size)
conv1 = Conv2D(64, (3, 3), activation='relu', padding='same')(input_layer)
conv2 = Conv2D(64, (3, 3), activation='relu', padding='same')(conv1)
flatten_layer = Flatten()(conv2)
dense1 = Dense(64, activation='relu')(flatten_layer)
dense2 = Dense(64, activation='relu')(dense1)
output_layer = Dense(action_space_size, activation='softmax')(dense2)
model = Model(inputs=input_layer, outputs=output_layer)
model.compile(optimizer=tf.keras.optimizers.legacy.Adam(learning_rate=0.1), loss=['categorical_crossentropy'], metrics=['accuracy'])






def create_new_model():
    new_model = Model(inputs=input_layer, outputs=output_layer)
    new_model.compile(optimizer=tf.keras.optimizers.legacy.Adam(learning_rate=0.1), loss=['categorical_crossentropy'], metrics=['accuracy'])
    return new_model

def train_model_self_play(num_games, model):
    for _ in range(num_games):
        play_game(model, model)

def play_game(model1, model2):
    board = chess.variant.GiveawayBoard()
    while not board.is_game_over():
        if board.turn == chess.WHITE:
            move = choose_action(board, model1, exploration_prob)
        else:
            move = choose_action(board, model2, exploration_prob)
        board.push(move)
    return board.result()

def train_new_player(best_player_model, new_player_model, threshold_win_rate=0.55, num_games=200):
    new_player_wins = 0
    for game in range(num_games):
        if random.choice([True, False]):
            result = play_game(new_player_model, best_player_model)
            if result == "1-0":
                new_player_wins += 1
        else:
            result = play_game(best_player_model, new_player_model)
            if result == "0-1":
                new_player_wins += 1

        win_rate = new_player_wins / (game + 1)
        if win_rate >= threshold_win_rate:
            print(f"New player has achieved a win rate of {win_rate}. It becomes the best player.")
            return new_player_model

    print(f"New player did not achieve the required win rate. Best player remains unchanged.")
    return best_player_model

# Load or create initial best player model
try:
    best_player_model = load_model("best_player.h5")
except IOError:
    print("No initial model found. Training a new model.")
    best_player_model = create_new_model()
    train_model_self_play(200, best_player_model)

# Main training and updating loop
while True:
    new_player_model = create_new_model()
    best_player_model = train_new_player(best_player_model, new_player_model)
    best_player_model.save("best_player.h5")
