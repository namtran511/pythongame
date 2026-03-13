import pygame
from game.constants import BTN_COLOR, BTN_HOVER, BTN_ACTIVE, BTN_TEXT


class Button:
    """A clickable rectangular button rendered with pygame."""

    def __init__(
        self,
        rect,
        text: str,
        font,
        color=None,
        hover_color=None,
        active_color=None,
        text_color=None,
        border_radius: int = 8,
    ):
        self.rect         = pygame.Rect(rect)
        self.text         = text
        self.font         = font
        self.color        = color        if color        is not None else BTN_COLOR
        self.hover_color  = hover_color  if hover_color  is not None else BTN_HOVER
        self.active_color = active_color if active_color is not None else BTN_ACTIVE
        self.text_color   = text_color   if text_color   is not None else BTN_TEXT
        self.border_radius = border_radius
        self._held = False

    # ─── Public API ───────────────────────────────────────────────────────────

    def handle_event(self, event) -> bool:
        """
        Feed a single pygame event.
        Returns True on the frame the button is released (clicked).
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._held = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._held and self.rect.collidepoint(event.pos):
                self._held = False
                return True
            self._held = False
        return False

    def draw(self, surface, mouse_pos) -> None:
        hovered = self.rect.collidepoint(mouse_pos)
        if self._held and hovered:
            bg = self.active_color
        elif hovered:
            bg = self.hover_color
        else:
            bg = self.color

        # Draw outer neon glow border (2px larger rect, brighter tinted color)
        glow_color = tuple(min(255, int(c * 1.6)) for c in bg)
        glow_rect  = self.rect.inflate(4, 4)
        pygame.draw.rect(surface, glow_color, glow_rect, 2,
                         border_radius=self.border_radius + 2)

        pygame.draw.rect(surface, bg, self.rect, border_radius=self.border_radius)

        # Inner bright highlight rim (1px, white-tinted)
        pygame.draw.rect(surface, (255, 255, 255, 30), self.rect, 1,
                         border_radius=self.border_radius)

        label = self.font.render(self.text, True, self.text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))

