import steam
import pygame
class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((800, 600), flags=pygame.SCALED)
        pygame.display.set_caption("Steamworks Test")

        self.clock = pygame.time.Clock()
        self.running = True
        # フォント設定
        self.font = pygame.font.Font("KH-Dot-Dougenzaka-12.ttf", 36)

        # 入力テキストの変数
        self.input_text = ""
        self.is_typing = False
        self.composition_text = ""  # IME変換中のバッファテキスト

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill("darkblue")

         # テキストボックスの描画
        pygame.draw.rect(surface, (200, 200, 200), (50, 75, 500, 50), border_radius=10)

        # 入力中のテキストを表示
        text_surface = self.font.render(self.input_text, True, (0, 0, 0))
        surface.blit(text_surface, (60, 85))
        # IME変換中のバッファテキスト描画（カーソルの右側に表示）
        composition_surface = self.font.render(self.composition_text, True, (100, 100, 100))  # グレー色で表示
        self.screen.blit(composition_surface, (60 + text_surface.get_width() + 5, 85))

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                # クリックで入力ボックスをアクティブ化
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if 50 <= x <= 550 and 75 <= y <= 125:
                        self.is_typing = True
                    else:
                        self.is_typing = False

                # IME変換確定時（確定したテキストを追加）
                if self.is_typing and event.type == pygame.TEXTINPUT:
                    self.input_text += event.text  # 確定した日本語を追加

                # IME入力中のバッファ表示（変換中の文字）
                if self.is_typing and event.type == pygame.TEXTEDITING:
                    self.composition_text = event.text  # 変換中の文字

                # バックスペース対応（確定済みの文字を削除）
                if self.is_typing and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        print("入力完了:", self.input_text)  # 確定したら表示
                        self.input_text = ""  # クリア

            self.update(dt)

            self.draw(self.screen)

if __name__ == "__main__":
    game = Game()
    game.run()

