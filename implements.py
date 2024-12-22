import math
import random
import time

import config

import pygame
from pygame.locals import Rect, K_LEFT, K_RIGHT


class Basic:
    def __init__(self, color: tuple, speed: int = 0, pos: tuple = (0, 0), size: tuple = (0, 0)):
        self.color = color
        self.rect = Rect(pos[0], pos[1], size[0], size[1])
        self.center = (self.rect.centerx, self.rect.centery)
        self.speed = speed
        self.start_time = time.time()
        self.dir = 270

    def move(self):
        dx = math.cos(math.radians(self.dir)) * self.speed
        dy = -math.sin(math.radians(self.dir)) * self.speed
        self.rect.move_ip(dx, dy)
        self.center = (self.rect.centerx, self.rect.centery)


class Block(Basic):
    def __init__(self, color: tuple, pos: tuple = (0,0), alive = True):
        super().__init__(color, 0, pos, config.block_size)
        self.pos = pos
        self.alive = alive

    def draw(self, surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect)
    
    def collide(self, blocks: list):
        # ============================================
        # TODO: Implement an event when block collides with a ball
        # 블록이 공과 충돌했을 대 이벤트 처리
        self.alive = False # 블록 제거
        if self in blocks:
            blocks.remove(self) # blocks 리스트에서 블록 삭제
        # 아이템 생성 (20% 확률)
        if random.random() < config.item_drop_prob:
            from __main__ import ITEMS  # 동적 import로 순환 참조 방지
            item_color = random.choice(config.item_colors)
            item = Item(item_color, self.rect.center)
            ITEMS.append(item)

class Paddle(Basic):
    def __init__(self):
        super().__init__(config.paddle_color, 0, config.paddle_pos, config.paddle_size)
        self.start_pos = config.paddle_pos
        self.speed = config.paddle_speed
        self.cur_size = config.paddle_size

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def move_paddle(self, event: pygame.event.Event):
        if event.key == K_LEFT and self.rect.left > 0:
            self.rect.move_ip(-self.speed, 0)
        elif event.key == K_RIGHT and self.rect.right < config.display_dimension[0]:
            self.rect.move_ip(self.speed, 0)

class Item(Basic):
    def __init__(self, color: tuple, pos: tuple):
        super().__init__(color, config.item_speed, pos, config.item_size)
    
    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)

    def collide_paddle(self, paddle: Paddle):
        # Paddle과 충돌 여부 확인
        return self.rect.colliderect(paddle.rect)


class Ball(Basic):
    def __init__(self, pos: tuple = config.ball_pos):
        super().__init__(config.ball_color, config.ball_speed, pos, config.ball_size)
        self.power = 1
        self.dir = 90 + random.randint(-45, 45)

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)

    def collide_block(self, blocks: list):
        # ============================================
        # TODO: Implement an event when the ball hits a block
        # 공이 블록과 부딪혔을 때 이벤트 처리
        for block in blocks[:]:
            # 블록 살아있는지 확인, 공과 블록 두 직사각형이 겹치는지 확인
            if block.alive and self.rect.colliderect(block.rect):
                # 충돌 위치(겹친 픽셀 수)
                overlap_left = self.rect.right - block.rect.left
                overlap_right = block.rect.right - self.rect.left
                overlap_top = self.rect.bottom - block.rect.top
                overlap_bottom = block.rect.bottom - self.rect.top

                # 가장 겹침이 작은 값 : 가장 빨리 충돌한 것
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                # 가로면 충돌 (상단 또는 하단)
                if min_overlap == overlap_top or min_overlap == overlap_bottom:
                    self.dir = 360 - self.dir
                # 세로면 충돌 (왼쪽 또는 오른쪽)
                elif min_overlap == overlap_left or min_overlap == overlap_right:
                    self.dir = 180 - self.dir
            
                # 블록의 collide 메서드 호출
                block.collide(blocks) # 블록 비활성화

                break # 첫 번재 충돌 후 반복 종료

    def collide_paddle(self, paddle: Paddle) -> None:
        if self.rect.colliderect(paddle.rect):
            self.dir = 360 - self.dir + random.randint(-5, 5)

    def hit_wall(self):
        # ============================================
        # TODO: Implement a service that bounces off when the ball hits the wall
        # 좌우 벽 충돌 => 반대방향으로 바꾸기
        if self.rect.left <= 0 or self.rect.right >= config.display_dimension[0]:
            self.dir = 180 - self.dir # 진행 방향 반대로 전환(좌우)
        
        # 상단 벽 충돌
        if self.rect.top <= 0:
            self.dir = 360 - self.dir # 진행 방향 반대로 전환(위 -> 아래)
    
    def alive(self):
        # ============================================
        # TODO: Implement a service that returns whether the ball is alive or not
        # 공이 아래쪽으로 빠진다면 False 반환, 그렇지 않으면 True 반환
            return self.rect.bottom < config.display_dimension[1]