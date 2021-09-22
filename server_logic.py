import random
from typing import List, Dict
from multiprocessing.pool import Pool

SEARCH_DEPTH = 10
MOVES = ["up", "down", "left", "right"]


class GameState:
    def __init__(self, data: dict):
        self.board_height = data["board"]["height"]
        self.board_width = data["board"]["width"]
        self.position = [(part["x"], part["y"]) for part in data["you"]["body"]]
        self.food = [(food["x"], food["y"]) for food in data["board"]["food"]]
        self.head = self.position[0]
        self.tail = self.position[-1]
        self.health = data["you"]["health"]
        self.history = []

    def step(self, move: str) -> None:
        if self.head in self.food:
            self.food.remove(self.head)
            self.history.append((None, self.health))
        else:
            self.history.append((self.position.pop(), self.health))

        x, y = 0, 0
        if move == "up":
            x = 0
            y = 1
        elif move == "down":
            x = 0
            y = -1
        elif move == "left":
            x = -1
            y = 0
        elif move == "right":
            x = 1
            y = 0

        self.head = (self.head[0] + x, self.head[1] + y)
        self.position.insert(0, self.head)

        # Snake eats food or tail moves
        if self.head in self.food:
            self.health = 100
        else:
            self.health -= 1

    def is_dead(self) -> bool:
        x, y = self.head
        return self.head in self.position[1:] \
               or not (0 <= x < self.board_width and 0 <= y < self.board_height) \
               or self.health <= 0

    def undo(self) -> None:
        tail, self.health = self.history.pop()

        self.position = self.position[1:]
        self.head = self.position[0]
        if tail:
            self.position.append(tail)
        else:
            self.food.append(self.head)


def backtrack(game_state: GameState):
    if game_state.is_dead():
        return len(game_state.history)
    if len(game_state.history) >= SEARCH_DEPTH:
        return SEARCH_DEPTH

    best_move = 0
    for move in MOVES:
        game_state.step(move)
        best_move = max(best_move, backtrack(game_state))
        game_state.undo()
        if best_move >= SEARCH_DEPTH:
            return SEARCH_DEPTH

    return best_move


def search(args: (GameState, str)) -> (str, int):
    game_state, move = args
    game_state.step(move)
    score = backtrack(game_state)
    print("Move", move, "Score", score)
    game_state.undo()
    return move, score


def pick_move(move_scores) -> str:
    return max(move_scores, key=lambda x: x[1])[0]
    # random.choices(possible_moves, weights=(move_scores[m] for m in possible_moves))[0]


def choose_move(data: dict) -> str:
    move_scores = {}

    game_state = GameState(data)

    with Pool(4) as pool:
        move_scores = pool.map(search, [(game_state, move) for move in MOVES])

    move = pick_move(move_scores)

    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked from all valid options in {possible_moves}")

    return move
