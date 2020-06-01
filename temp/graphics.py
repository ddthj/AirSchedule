import pygame
from vec2 import Vec2


class Element:
    def __init__(self, parent=None, **kwargs):
        self.color = kwargs.get("color", (0, 0, 0))
        self.align = kwargs.get("align", "none")
        self.padding = Vec2(kwargs.get("padding", (0, 0)))
        self.size = Vec2(kwargs.get("size", (0, 0)))
        self.border = kwargs.get("border", 0)

        self.text = kwargs.get("text", "")
        self.font = kwargs.get("font", None)

        self.handler = kwargs.get("handler", None)
        self.visible = kwargs.get("visible", True)

        self.parent = parent
        self.location = None
        self.text = None

    def get_loc(self):
        if self.location is None:
            if self.parent is None:
                self.location = self.padding
                return self.padding
            else:
                m_half = self.size / 2
                p_loc = self.parent.get_loc()
                p_half = self.parent.size / 2
                if self.align == "none":
                    align = Vec2(0,0)
                elif self.align == "center":
                    align = p_half - m_half
                elif self.align == "left":
                    align = (p_half * Vec2(0, 1)) - (m_half * Vec2(0, 1))
                elif self.align == "right":
                    align = (p_half * Vec2(2, 1)) - (m_half * Vec2(2, 1))
                elif self.align == "top":
                    align = (p_half * Vec2(1, 0)) - (m_half * Vec2(1, 0))
                elif self.align == "bottom":
                    align = (p_half * Vec2(1, 2)) - (m_half * Vec2(1, 2))
                else:
                    align = Vec2(0, 0)
                self.location = p_loc + align + self.padding
        return self.location

    def update(self, client, events):
        if self.handler is not None:
            self.handler(self, client, events)

    def render(self, window):
        if self.visible:
            pygame.draw.rect(window, self.color, (*self.location, *self.size), self.border)


class Gui:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.resolution = (1920, 1050)
        self.window = pygame.display.set_mode(self.resolution, pygame.RESIZABLE)
        pygame.display.set_caption("AirSchedule")
        pygame.display.set_icon(pygame.image.load("icon.png"))
        self.bg_color = (100, 100, 100)
        self.font_15 = pygame.font.SysFont("courier", 15)
        self.font_25 = pygame.font.SysFont("courier", 25)
        self.font_30 = pygame.font.SysFont("courier", 30)
        self.quit = False
