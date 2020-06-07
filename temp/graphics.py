import pygame
from vec2 import Vec2


class Element:
    def __init__(self, parent=None, **kwargs):
        self.size = Vec2(kwargs.get("size", (0, 0)))
        self.align = kwargs.get("align", "none")
        self.padding = Vec2(kwargs.get("padding", (0, 0)))
        self.border = kwargs.get("border", 0)
        self.color = kwargs.get("color", (0, 0, 0))

        self.text = kwargs.get("text", "")
        self.text_align = kwargs.get("text-align", "center")
        self.text_padding = kwargs.get("text-padding", Vec2(0, 0))
        self.font = kwargs.get("font", None)
        self.text_color = kwargs.get("text-color", (0, 0, 0))

        self.handler = kwargs.get("handler", None)
        self.visible = kwargs.get("visible", True)

        self.parent = parent
        if self.size == (0, 0):
            if self.parent is not None:
                self.size = self.parent.size
            else:
                self.size = Vec2(1920, 1050)
        self.location = None
        self.rendered_text, self.text_location = self.prep_text()

    def get_loc(self):
        if self.location is None:
            if self.parent is None:
                self.location = self.padding.copy()
            else:
                m_half = self.size / 2
                p_loc = self.parent.get_loc()
                p_half = self.parent.size / 2
                if self.align == "none":
                    align = Vec2(0, 0)
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

    def prep_text(self):
        if len(self.text) > 0:
            if self.font is not None:
                rendered = self.font.render(self.text, 1, self.text_color)
                m_half = Vec2(rendered.get_rect().width, rendered.get_rect().height) / 2
                p_half = self.size / 2
                if self.text_align == "left":
                    align = (p_half * Vec2(0, 1)) - (m_half * Vec2(0, 1))
                elif self.text_align == "right":
                    align = (p_half * Vec2(2, 1)) - (m_half * Vec2(2, 1))
                else:
                    align = p_half - m_half
                text_location = self.get_loc() + align + self.text_padding
                return rendered, text_location
            else:
                raise AttributeError("Element with text has no defined font")
        else:
            return None, None

    def update(self, client, events):
        if self.handler is not None:
            return self.handler(self, client, events)
        return []

    def render(self, window):
        if self.visible:
            pygame.draw.rect(window, self.color, (*self.get_loc(), *self.size), self.border)
            if self.rendered_text is not None:
                window.blit(self.rendered_text, self.text_location.render())


class FlightElement(Element):
    def __init__(self, parent=None, **kwargs):
        """
        todo - find out why this is an error, and customize rendering for this element
         also make the the methods in the client Flight class for doing this properly
        """
        super().__init__(parent, kwargs)
        self.dept_text = kwargs.get("dept_text", "")
        self.dept_time = kwargs.get("dept_time", "")
        self.arri_text = kwargs.get("arri_text", "")
        self.arri_time = kwargs.get("arri_time", "")
        self.side_font = kwargs.get("font", None)


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

        self.elements = []
        self.clock = pygame.time.Clock()

    def connecting_page(self):
        self.elements = [Element(
            parent=None,
            color=(150, 150, 150),
            text="Connecting...",
            font=self.font_30
        )]

    def connecting_failed_page(self):
        self.elements = [Element(
            parent=None,
            color=(150, 150, 150),
            text="Connection Failed",
            font=self.font_30
        )]

    def schedule_page(self, client):
        self.elements = []
        for i in range(1, len(client.objects["aircraft"]) + 1):
            if i - 1 < len(client.objects["aircraft"]):
                text = client.objects["aircraft"][i - 1].tail_number
            else:
                text = ""
            self.elements.append(
                Element(size=Vec2(100, 35),
                        padding=Vec2(0, i * 35),
                        color=(150, 150, 150),
                        text=text,
                        font=self.font_15
                        ))
            # todo - turn aircraft and flight into children of element, use them here instead
            self.elements.append(
                Element(size=Vec2(self.resolution[0], 35),
                        padding=Vec2(0, (i - 1) * 35),
                        color=(0, 0, 0),
                        border=1,
                        ))

    def update(self, client):
        self.clock.tick()
        print(self.clock.get_time())
        self.window.fill(self.bg_color)
        requests = []
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.quit = True

        for element in self.elements:
            requests += element.update(client, events)
            element.render(self.window)
        pygame.display.update()
        return requests
