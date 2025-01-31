# **サーバー or クライアントを決める**
from SnakeGame.SnakeGame import SnakeGame
if __name__ == "__main__":
    is_server = input("サーバーを起動しますか？ (y/n): ").strip().lower() == "y"
    game = SnakeGame(is_server)
    game.run()
