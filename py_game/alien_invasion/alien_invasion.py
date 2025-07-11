import sys
import pygame

from settings import Settings
from ship import Ship
from bullet import Bullet

class AlienInvasion:

    def __init__(self):

        pygame.init()
        self.clock = pygame.time.Clock()

        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
            # (0, 0), pygame.FULLSCREEN
        )  # 创建一个(1200, 800)的显示窗口
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height

        pygame.display.set_caption('Alien Invasion')

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()

    def run_game(self):
        while True:
            # 侦听事件
            self._check_events()
            self.ship.update()
            self._update_bullets()
            # 更新界面
            self._update_screen()
            self.clock.tick(60)     # 尽力保证每秒刷新60次

    def _check_events(self):
        # 响应事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _update_screen(self):
        # 刷新界面
        # fill()方法用于处理surface,只接受一个表示颜色的实参
        self.screen.fill(self.settings.bg_color)# 每次循环时使用bg_color重新填充
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        # 将飞船绘制到surface
        self.ship.blitme()

        pygame.display.flip()

    def _check_keydown_events(self, event): # 为什么可以这么写呢,是应为按下每个键都属于不同的event
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False

    def _fire_bullet(self):

        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        self.bullets.update()

        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
