from typing import List
import pygame
from common import WHITE, BACKGROUND_SPRITE, FPS, screen, clock
from entities import (
    Player, Robot,
    GameItem, ItemType, NPC, GameState, GameStateType,
)
from utils import overlap


# Game States:
player: Player = Player(350, 200)

list_robot: List[Robot] = [
    Robot(500, 500, 1, 1),
    Robot(50, 50, -2, 2),
    Robot(50, 10, 3, 5),
    Robot(500, 0, 9, 5),
    Robot(100, 50, 3, 10),
    Robot(590, 10, -8, 1)
]

list_item: List[GameItem] = [
    GameItem(600, 500, ItemType.DIAMOND_BLUE),
    GameItem(800, 500, ItemType.DIAMOND_RED),
    GameItem(1000, 400, ItemType.DIAMOND_RED),
    GameItem(100, 500, ItemType.DIAMOND_BLUE),
    GameItem(880, 700, ItemType.DIAMOND_RED),
    GameItem(500, 400, ItemType.DIAMOND_RED),
]

to_mo: NPC = NPC(1000, 50)

# Bắt đầu game
game_state: GameState = GameState(score=0)

running: bool = True
while running:
    # Người chơi có tắt màn hình game chưa
    if pygame.event.peek(pygame.QUIT):
        running = False
        break

    # ----------------------------------------
    if game_state.state == GameStateType.RUNNING:
        player.update()

        for robot in list_robot:
            robot.update()

        for item in list_item:
            if not item.hidden:
                if overlap(player.x, player.y, player.image, item.x, item.y, item.image):
                    item.set_hidden()
                    # Increase Score
                    new_score: int = game_state.score + 1
                    game_state.update_score(new_score)

        for robot in list_robot:
            if overlap(player.x, player.y, player.image, robot.x, robot.y, robot.image):
                print("YOU LOST!!")
                game_state.update_state(GameStateType.LOST)

        if overlap(player.x, player.y, player.image, to_mo.x, to_mo.y, to_mo.image):
            print("YOU WON!!")
            game_state.update_state(GameStateType.WON)

    # ----------------------------------------
    # Vẽ các vật phẩm game
    screen.fill(WHITE)
    screen.blit(BACKGROUND_SPRITE, (0, 0))

    player.render(screen)

    for robot in list_robot:
        robot.render(screen)

    for item in list_item:
        item.render(screen)

    to_mo.render(screen)

    game_state.render(screen)

    pygame.display.flip()
    clock.tick(FPS)

# Ket thuc game
pygame.quit()
