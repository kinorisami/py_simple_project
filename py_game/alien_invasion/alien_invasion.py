import sys
from time import sleep
import pygame

from game_stats import GameStats
from alien import Alien
from settings import Settings
from ship import Ship
from bullet import Bullet
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:

    def __init__(self):

        pygame.init()
        self.clock = pygame.time.Clock()
        self.game_active = False
        self.settings = Settings()


        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
            # (0, 0), pygame.FULLSCREEN
        )  # 创建一个(1200, 800)的显示窗口
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height
        self.play_button = Button(self, 'Play')
        pygame.display.set_caption('Alien Invasion')

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self._create_fleet()

    def run_game(self):
        while True:
            # 侦听事件
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            # 更新界面
            self._update_screen()
            self.clock.tick(60)     # 尽力保证每秒刷新60次

    def _update_screen(self):
        # 刷新界面
        # fill()方法用于处理surface,只接受一个表示颜色的实参
        self.screen.fill(self.settings.bg_color)  # 每次循环时使用bg_color重新填充
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        # 将飞船绘制到surface
        self.ship.blitme()
        # 绘制外星人
        self.aliens.draw(self.screen)

        self.sb.show_score()

        if not self.game_active:
            self.play_button.draw_button()

        pygame.display.flip()


    # 键盘事件
    def _check_events(self):
        # 响应事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()  # 返回一个玩家单击时的光标坐标tuple
                self._check_play_button(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
    # 鼠标
    def _check_play_button(self, mouse_pos):

        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_ships()
            self.game_active = True
            self.bullets.empty()
            self.aliens.empty()

            self._create_fleet()
            self.ship.blitme()
            pygame.mouse.set_visible(False)

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


    # 子弹
    def _fire_bullet(self):

        if len(self.bullets) < self.settings.bullets_allowed and self.game_active:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        self.bullets.update()
        # 遍历子弹 将超出屏幕上界的子弹remove
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()


    # 外星人
    def _create_fleet(self):

        # 通过实例化一个Alien来获取矩形宽度
        alien = Alien(self)
        alien_width, alien_height = alien.rect.width, alien.rect.height

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width -  alien_width * 2):

                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            current_y += 2 * alien_height
            current_x = alien_width

    def _create_alien(self, x_position, y_position):
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.y = y_position
        new_alien.rect.x = new_alien.x
        new_alien.rect.y = new_alien.y
        self.aliens.add(new_alien)

    def _update_aliens(self):

        self._check_fleet_edges()
        self.aliens.update()

        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            # 返回精灵或者None
            self._ship_hit()

        self._check_aliens_bottom()

    def _check_fleet_edges(self):

        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):

        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


    # 子弹和alien的碰撞逻辑
    def _check_bullet_alien_collisions(self):
        # 检查bullet和alien是否有碰撞 返回一个字典, key is bullet, alien is value, 并删除后面两个参数就是
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            # 如果一个子弹击中了多个alien, 击中数不可以使用简单的len(collisions)
            hit_count = sum(len(aliens_hit) for aliens_hit in collisions.values())
            # aliens_hit也是一个列表,collisions.values()是有字典值组成的列表的列表
            self.stats.score += self.settings.alien_points * hit_count
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            self.stats.level += 1
            self.sb.prep_level()

    # alien和 ship 碰撞
    def _ship_hit(self):

        if self.stats.ships_left - 1 > 0:

            self.stats.ships_left -= 1
            self.sb.prep_ships()
            self.bullets.empty()
            self.aliens.empty()

            self._create_fleet()
            self.ship.center_ship()

            sleep(0.5)
        else:
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            self.game_active = False
            pygame.mouse.set_visible(True)

    # 检查alien是否到达下边界
    def _check_aliens_bottom(self):
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:

                self._ship_hit()
                break

if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
