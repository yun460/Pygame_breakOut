import sys
from implements import Basic, Block, Paddle, Ball
import config

import pygame
from pygame.locals import QUIT, Rect, K_ESCAPE, K_SPACE


pygame.init()
pygame.key.set_repeat(3, 3)
surface = pygame.display.set_mode(config.display_dimension)

fps_clock = pygame.time.Clock()

paddle = Paddle()
ball1 = Ball()
BLOCKS = []
ITEMS = []
BALLS = [ball1]
life = config.life
start = False


def create_blocks():
    for i in range(config.num_blocks[0]):
        for j in range(config.num_blocks[1]):
            x = config.margin[0] + i * (config.block_size[0] + config.spacing[0])
            y = (
                config.margin[1]
                + config.scoreboard_height
                + j * (config.block_size[1] + config.spacing[1])
            )
            color_index = j % len(config.colors)
            color = config.colors[color_index]
            block = Block(color, (x, y))
            BLOCKS.append(block)

MAX_BALLS = 10

def tick():
    global life
    global BLOCKS
    global ITEMS
    global BALLS
    global paddle
    global ball1
    global start
    global cur_score
    cur_score = config.num_blocks[0] * config.num_blocks[1] - len(BLOCKS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:  # ESC 키가 눌렸을 때
                pygame.quit()
                sys.exit()
            if event.key == K_SPACE:  # space키가 눌려지만 start 변수가 True로 바뀌며 게임 시작
                start = True
            paddle.move_paddle(event)

    for item in ITEMS[:]:
        item.move()
        if item.collide_paddle(paddle):
            # Paddle과 아이템이 충돌했을 때 처리
            if item.color == (255, 0, 0):  # 빨간색 아이템
                # 빨간색 아이템 효과: 예를 들어 점수 증가
                pass
            elif item.color == (0, 0, 255):  # 파란색 아이템
                # 파란색 아이템 효과: 예를 들어 공 추가
                # 파란색 아이템 효과: 공 3개로 만들기
                if len(BALLS) < MAX_BALLS:  # 공의 개수가 최대 개수 이하일 때만 추가
                    new_balls = []
                    for ball in BALLS:  # 기존 공을 3배로 만들기
                        if len(BALLS) + 2 <= MAX_BALLS:  # 최대 개수에 도달하면 복제하지 않음
                            for _ in range(2):  # 기존 공을 복제해서 3개로 만들기
                                new_ball = Ball(pos=ball.rect.center)  # 기존 공 위치에서 새로운 공 생성
                                new_balls.append(new_ball)
                    BALLS.extend(new_balls)  # 새로운 공들을 BALLS 리스트에 추가

        
            ITEMS.remove(item)  # 아이템 제거
        elif item.rect.top > config.display_dimension[1]:  # 화면 밖으로 나간 경우
            ITEMS.remove(item)

    for ball in BALLS:
        if start:
            ball.move()
        else:
            ball.rect.centerx = paddle.rect.centerx
            ball.rect.bottom = paddle.rect.top

        ball.collide_block(BLOCKS)
        ball.collide_paddle(paddle)
        ball.hit_wall()
        if ball.alive() == False:
            BALLS.remove(ball)


def main():
    global life
    global BLOCKS
    global ITEMS
    global BALLS
    global paddle
    global ball1
    global start
    my_font = pygame.font.SysFont(None, 50)
    mess_clear = my_font.render("Cleared!", True, config.colors[2])
    mess_over = my_font.render("Game Over!", True, config.colors[2])
    create_blocks()
    
    while True:
       
        tick()
        surface.fill((0, 0, 0))
        for item in ITEMS:
            item.draw(surface)
        paddle.draw(surface)

        for block in BLOCKS:
            block.draw(surface)

        

        score_txt = my_font.render(f"Score : {cur_score * 10}", True, config.colors[2])
        life_font = my_font.render(f"Life: {life}", True, config.colors[0])

        surface.blit(score_txt, config.score_pos)
        surface.blit(life_font, config.life_pos)

        if len(BALLS) == 0:
            if life > 1:
                life -= 1
                ball1 = Ball()
                BALLS = [ball1]
                start = False
            else:
                surface.blit(mess_over, (200, 300))
        elif all(block.alive == False for block in BLOCKS):
            surface.blit(mess_clear, (200, 400))
        else:
            for ball in BALLS:
                if start == True:
                    ball.move()
                ball.draw(surface)
            for block in BLOCKS:
                block.draw(surface)

        pygame.display.update()
        fps_clock.tick(config.fps)


if __name__ == "__main__":
    main()
