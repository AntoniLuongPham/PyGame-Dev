from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List, Optional, Sequence

import pygame

from common import util
from common.event import EventType, GameEvent
from common.types import EntityType
from config import GameConfig
from entities.animated_entity import AnimatedEntity
from entities.friendly_npc import FriendlyNpc

if TYPE_CHECKING:
    from worlds.world import World

logger = util.get_logger(__name__)


class Player(AnimatedEntity):
    """
    The main character controlled by user, can talk / fight NPCs, can interact with in-game objects.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.npc_near_by: Optional[FriendlyNpc] = None
        self.talking: bool = False
        self.inventory: List = []
        self.inventory_entity_id: Optional[int] = None

        self.last_hit_t: int = pygame.time.get_ticks()

    def update(self, events: Sequence[GameEvent], world: World) -> None:
        super().update(events, world)
        self._update_npc_near_by()
        self._pick_item_near_by()
        self._handle_events()
        self._update_screen_offset()

        # Manage the dependent entities.
        self._update_inventory_entity()

    def _update_inventory_entity(self):
        """
        This Player entity directly manages a PlayerInventory entity.
        """
        if not self.inventory_entity_id:
            self.inventory_entity_id = self.world.add_entity(EntityType.PLAYER_INVENTORY)
        self.world.get_entity(self.inventory_entity_id).set_inventory(self.inventory)

    def _handle_events(self):
        """
        This subject is controllable by user, we ask it to move based on keyboard inputs here.
        """
        for event in self.events:

            # Only allow player to move when not talking to some NPC.
            if not self.talking:
                if event.is_key_down(pygame.K_LEFT, pygame.K_a):
                    self.move_left(True)
                elif event.is_key_down(pygame.K_RIGHT, pygame.K_d):
                    self.move_right(True)
                elif event.is_key_down(pygame.K_UP, pygame.K_SPACE, pygame.K_w):
                    self.jump()

            if event.is_key_up(pygame.K_LEFT, pygame.K_a):
                self.move_left(False)
            elif event.is_key_up(pygame.K_RIGHT, pygame.K_d):
                self.move_right(False)
            elif event.is_key_up(pygame.K_e):
                self._handle_activation()
            elif event.is_type(EventType.NPC_DIALOGUE_END):
                self.talking = False

    def _handle_activation(self):
        if not self.npc_near_by or not self.npc_near_by.has_dialogue():
            return
        # Broadcast an event for the NPC to handle
        # logger.info(f"_handle_activation with: {self.npc_near_by.entity_type}")
        GameEvent(EventType.PLAYER_ACTIVATE_NPC, listener_id=self.npc_near_by.id).post()
        self.talking = True  # this will turn back to False when receiving event NPC_DIALOGUE_END

    def _update_npc_near_by(self):
        self.npc_near_by = None
        for npc in self.world.get_friendly_npcs():
            if self.collide(npc):
                # Get a hold of the NPC, and post an event for that NPC to handle
                self.npc_near_by = npc
                GameEvent(EventType.PLAYER_NEAR_NPC, listener_id=npc.id).post()
                break

    def _pick_item_near_by(self):
        """
        If Player collides with a collectable entity, remove that entity from World,
        while adding that entity to the self.inventory list.
        """
        for entity in self.world.get_collectable_tiles():
            if self.collide(entity):
                self.world.remove_entity(entity.id)
                self.inventory.append(entity)
                logger.info(f"Player picked up 1 {entity.entity_type}")

    def _update_screen_offset(self):
        """Logics for horizontal world scroll based on player movement"""
        delta_screen_offset = 0

        at_right_edge = self.rect.right >= GameConfig.WIDTH
        at_right_soft_edge = self.rect.right > GameConfig.WIDTH - GameConfig.PLAYER_SOFT_EDGE_WIDTH
        at_left_edge = self.rect.left <= 0
        at_left_soft_edge = self.rect.left < GameConfig.PLAYER_SOFT_EDGE_WIDTH

        if (
            at_left_edge
            or at_right_edge
            or (at_left_soft_edge and not self.world.at_left_most())
            or at_right_soft_edge
        ):
            # Undo player position change (player walks in-place)
            self.rect.x -= self.dx
            delta_screen_offset = -self.dx

        self.world.update_screen_offset(delta_screen_offset)
