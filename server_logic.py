import random
from typing import List, Dict

"""
This file can be a nice home for your move logic, and to write helper functions.

We have started this for you, with a function to help remove the 'neck' direction
from the list of possible moves!
"""


def avoid_my_neck(my_head: Dict[str, int], my_body: List[dict], possible_moves: List[str]) -> List[str]:
    """
    my_head: Dictionary of x/y coordinates of the Battlesnake head.
            e.g. {"x": 0, "y": 0}
    my_body: List of dictionaries of x/y coordinates for every segment of a Battlesnake.
            e.g. [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]
    possible_moves: List of strings. Moves to pick from.
            e.g. ["up", "down", "left", "right"]

    return: The list of remaining possible_moves, with the 'neck' direction removed
    """
    my_neck = my_body[1]  # The segment of body right after the head is the 'neck'

    if my_neck["x"] < my_head["x"]:  # my neck is left of my head
        possible_moves.remove("left")
    elif my_neck["x"] > my_head["x"]:  # my neck is right of my head
        possible_moves.remove("right")
    elif my_neck["y"] < my_head["y"]:  # my neck is below my head
        possible_moves.remove("down")
    elif my_neck["y"] > my_head["y"]:  # my neck is above my head
        possible_moves.remove("up")

    return possible_moves

def avoid_edge(data: dict, new_heads: dict, possible_moves: List[str]) -> List[str]:
  board_height = data["board"]["height"]
  board_width = data["board"]["width"]

  if new_heads["left"]["x"] < 0:
    possible_moves.remove("left")
  if board_width <= new_heads["right"]["x"]:
    possible_moves.remove("right")
  if new_heads["down"]["y"] < 0:
    possible_moves.remove("down")
  if board_height <= new_heads["up"]["y"]:
    possible_moves.remove("up")

  return possible_moves

def new_head_positions(my_head: Dict[str, int], possible_moves: List[str]) -> Dict[str, Dict[str, int]]:
  new_heads = {}

  for move in possible_moves:
    if move == "left":
      new_heads[move] = {"x": my_head["x"] - 1, "y": my_head["y"]}
    elif move == "right": 
      new_heads[move] = {"x": my_head["x"] + 1, "y": my_head["y"]}
    elif move == "up":
      new_heads[move] = {"x": my_head["x"], "y": my_head["y"] + 1}
    elif move == "down":
      new_heads[move] = {"x": my_head["x"], "y": my_head["y"] - 1}
    
  return new_heads

def avoid_body(data: dict, new_heads: dict, possible_moves: List[str]) -> List[str]:
  return list(filter(lambda m: all(new_heads[m] != part for part in data["you"]["body"]), possible_moves))

def avoid_snakes(data: dict, new_heads: dict, possible_moves: List[str]) -> List[str]:
  for snake in data["board"]["snakes"]:
    possible_moves = list(filter(lambda m: all(new_heads[m] != part for part in snake["body"]), possible_moves))
  return possible_moves

def score_moves(data: dict, my_head: Dict[str, int], new_heads: dict, possible_moves: List[str]) -> Dict[str, int]:
  if len(possible_moves) == 0: return {}

  foods = data["board"]["food"]

  # scores start with lower being better
  move_scores = { m : 1000 for m in possible_moves }
  
  for food in foods:
    for move in possible_moves:
      distance_sq = (food["x"] - new_heads[move]["x"]) ** 2 + (food["y"] - new_heads[move]["y"]) ** 2
      if distance_sq < move_scores[move]:
        move_scores[move] = distance_sq

  # invert scores so higher better
  worst_score = max(move_scores.values())
  for score in move_scores:
    move_scores[score] = abs(move_scores[score] - worst_score)
  
  return move_scores

def pick_move(possible_moves: List[str], move_scores: Dict[str, int]) -> str:
  return random.choices(possible_moves, weights=(move_scores[m] for m in possible_moves))[0]

def valid_directions(data: dict, position: dict) -> List[str]:
  directions = ["up", "down", "left", "right"]
  new_positions = new_head_positions(position, directions)
  directions = avoid_edge(data, new_positions, directions)
  return avoid_snakes(data, new_positions, directions)

def bfs(data: dict, my_head: Dict[str, int], limit: int) -> List[str]:
  fringe = {}
  visited = {}

  directions = valid_directions(data, my_head)
  new_heads = new_head_positions(my_head, directions) 
  for direction in directions:
    fringe[direction] = [new_heads[direction]]
    visited[direction] = []

  while any(0 < len(x) for x in fringe.values()):
    search(data, fringe, visited, directions, limit)
    
  # directions we want to consider moved in search so add back
  directions = valid_directions(data, my_head) 
  good_directions = []

  # find directions which have at least enough space for length of snake,
  # or if not possible find the direction with most space
  if 0 < len(directions):
    good_directions = list(filter(lambda x: limit <= len(visited[x]), directions))
    if len(good_directions) == 0:
      best_direction = directions[0]
      for x in directions:
        if len(visited[best_direction]) < len(visited[x]):
          best_direction = x
      good_directions = [best_direction]
  return good_directions
    

def search(data: dict, fringe: dict, visited: dict, directions: List[str], limit: int) -> None:
  for i in range(len(directions)):
    direction = directions[i]
    if fringe[direction]:
      current = fringe[direction].pop()
      for j in range(len(directions)):
        if i != j:
          if current in visited[directions[j]]:
            fringe[direction] += fringe[directions[j]]
            visited[direction] += visited[directions[j]]
            visited[directions[j]] = visited[direction]
            fringe[directions[j]].clear()
            directions.remove(directions[j]) # helps with latency
            return

      visited[direction].append(current)

      if limit < len(visited[direction]):
        fringe[direction].clear()
        return
      neighbors = expandBFS(data, current) 
      neighbors = list(filter(lambda x: not x in visited[direction], neighbors))
      fringe[direction] += neighbors
  return
    
def expandBFS(data: dict, position: dict) -> List[Dict[str, int]]: 
  directions = valid_directions(data, position)
  head_set = list(new_head_positions(position, directions).values())
  return head_set 


def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request

    return: A String, the single move to make. One of "up", "down", "left" or "right".

    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.

    """
    my_head = data["you"]["head"]  # A dictionary of x/y coordinates like {"x": 0, "y": 0}
    my_body = data["you"]["body"]  # A list of x/y coordinate dictionaries like [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]

    # TODO: uncomment the lines below so you can see what this data looks like in your output!
    # print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    # print(f"All board data this turn: {data}")
    # print(f"My Battlesnakes head this turn is: {my_head}")
    # print(f"My Battlesnakes body this turn is: {my_body}")

    # If snake didn't eat, move tail
    if data["you"]["shout"] != "Yummy chicken":
      removed = data["you"]["body"].pop()
      print("Removed tail at:", removed)
    

    # TODO: stop collision after eating food.
    # When food eaten, head moves extra step in current direction which can cause collisions.
    possible_moves = bfs(data, my_head, data["you"]["length"])
    # possible_moves = bfs(data, my_head, 2) 
    print("Possible moves:", possible_moves)

    if len(possible_moves) == 0:
      print("No moves, going basic")
      possible_moves = valid_directions(data, my_head)
    

    new_heads = new_head_positions(my_head, possible_moves)
    move_scores = score_moves(data, my_head, new_heads, possible_moves)

    move = pick_move(possible_moves, move_scores)

    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked from all valid options in {possible_moves}")

    print(data["you"]["shout"])
    shout = ""

    if new_heads[move] in data["board"]["food"]:
      shout = "Yummy chicken"


    return {"move": move, "shout": shout}
