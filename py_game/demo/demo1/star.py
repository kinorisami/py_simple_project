import pygame
import random
import os

# 星星精灵类
class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = star_img
        self.rect = self.image.get_rect(topleft=(x, y))

# 初始化
pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("随机放置图像星星")
clock = pygame.time.Clock()
color = (255, 255, 255)
# 加载星星图片
star_img = pygame.image.load("img.png").convert_alpha()
star_width, star_height = star_img.get_size()


# 星星组
stars = pygame.sprite.Group()

# 随机生成不重叠的星星
def create_non_overlapping_stars(group, num_stars, max_tries=1000):
    attempts = 0
    while len(group) < num_stars and attempts < max_tries:
        x = random.randint(0, 600 - star_width)
        y = random.randint(0, 400 - star_height)
        new_star = Star(x, y)
        if not pygame.sprite.spritecollideany(new_star, group):
            group.add(new_star)
        attempts += 1

create_non_overlapping_stars(stars, 20)

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(color)  # 白色背景
    stars.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
