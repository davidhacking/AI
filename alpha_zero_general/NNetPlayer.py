from chinese_chess.ChineseChessGame import ChineseChessGame
from chinese_chess.ChineseChessPlayers import *
from utils import *
from chinese_chess.pytorch.NNet import NNetWrapper as nn
from MCTS import MCTS
import multiprocessing
from tqdm import tqdm

class NNetPlayer():
    def __init__(self, game, model_path, model_file):
        self.game = game
        n1 = nn(game)
        if model_file:
            n1.load_checkpoint(model_path, model_file)
        args1 = dotdict({'numMCTSSims': 50, 'cpuct':1.0, 'max_mcts_depth': 500})
        self.mcts = MCTS(game, n1, args1)

    def play(self, board):
        actions = self.mcts.getActionProb(board, temp=0)
        a = np.argmax(actions)
        valids = self.game.getValidMoves(board, 1)
        if valids[a] == 0:
            self.game.display(board)
            move = self.game.action_to_move(board, a)
            x1, y1, x2, y2 = int(move[0]), int(move[1]), int(move[2]), int(move[3])
            print(f"ai play {a} {x1},{y1} -> {x2},{y2}")
            assert valids[a] > 0
        return a

def playGame(game, player1, player2):
    players = [player2, None, player1]
    curPlayer = 1
    board = game.getInitBoard()
    it = 0
    
    while game.getGameEnded(board, curPlayer) == 0:
        it += 1
        action = players[curPlayer + 1].play(game.getCanonicalForm(board, curPlayer))
        valids = game.getValidMoves(game.getCanonicalForm(board, curPlayer), 1)

        if valids[action] == 0:
            logging.error(f'Action {action} is not valid!')
            assert valids[action] > 0

        board, curPlayer = game.getNextState(board, curPlayer, action)
    return curPlayer * game.getGameEnded(board, curPlayer)

def worker(args):
    count1, count2, model_path1, model_file1, model_path2, model_file2 = args
    game = ChineseChessGame()
    oneWon = 0
    twoWon = 0
    draws = 0
    
    # Player1 先手的对局
    for _ in range(count1):
        player1 = NNetPlayer(game, model_path1, model_file1)
        player2 = NNetPlayer(game, model_path2, model_file2)
        result = playGame(game, player1, player2)
        if result == 1:
            oneWon += 1
        elif result == -1:
            twoWon += 1
        else:
            draws += 1
    
    # Player2 先手的对局
    for _ in range(count2):
        player1 = NNetPlayer(game, model_path1, model_file1)
        player2 = NNetPlayer(game, model_path2, model_file2)
        result = playGame(game, player2, player1)
        if result == 1:    # player2作为先手获胜
            twoWon += 1
        elif result == -1: # player2作为先手失败
            oneWon += 1
        else:
            draws += 1
            
    return (oneWon, twoWon, draws)

def parallelPlayGames(num, model_path1, model_file1, model_path2, model_file2, num_processes=4):
    if num % (2 * num_processes) != 0:
        raise ValueError("num必须能被2*num_processes整除")
    
    num_half = num // 2
    chunk = num_half // num_processes
    
    ctx = multiprocessing.get_context('spawn')
    with ctx.Pool(num_processes) as pool:
        args = [(chunk, chunk, model_path1, model_file1, model_path2, model_file2)] * num_processes
        results = list(tqdm(pool.imap(worker, args), total=num_processes, desc="并行对局"))
    
    total_oneWon = sum(r[0] for r in results)
    total_twoWon = sum(r[1] for r in results)
    total_draws = sum(r[2] for r in results)
    
    return total_oneWon, total_twoWon, total_draws

if __name__ == "__main__":
    model_path = '/workspace/alpha_zero/chinese_chess_models/'
    model1 = 'pretrained_3.pth.tar'
    model2 = ''
    
    total_games = 20  # 需要是2*num_processes的整数倍
    num_processes = 10
    
    oneWon, twoWon, draws = parallelPlayGames(
        total_games,
        model_path, model1,
        model_path, model2,
        num_processes
    )
    
    print(f"Player1 胜利: {oneWon} 次")
    print(f"Player2 胜利: {twoWon} 次")
    print(f"平局: {draws} 次")