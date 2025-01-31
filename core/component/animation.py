import pygame

class Animation:
    """単一のアニメーションを管理"""
    def __init__(self, sprite_sheet, frame_width, frame_height, frame_count, frame_duration):
        """
        :param sprite_sheet: スプライトシート画像
        :param frame_width: フレームの幅
        :param frame_height: フレームの高さ
        :param frame_count: フレームの総数
        :param frame_duration: 1フレームの時間 (秒)
        """
        self.sprite_sheet = sprite_sheet
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames = [self.get_frame(i) for i in range(frame_count)]
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.time_elapsed = 0

    def get_frame(self, index):
        """スプライトシートからフレームを抽出"""
        x = index * self.frame_width
        return self.sprite_sheet.subsurface(pygame.Rect(x, 0, self.frame_width, self.frame_height))

    def update(self, delta_time):
        """アニメーションの更新"""
        self.time_elapsed += delta_time
        if self.time_elapsed >= self.frame_duration:
            self.time_elapsed = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def get_current_frame(self):
        """現在のフレームを取得"""
        return self.frames[self.current_frame]
