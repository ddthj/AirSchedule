import pygame
from vec2 import Vec2


def scroll_handler(element, client, gui):
    scroll_dif = gui.scroll - element.scroll_distance
    if scroll_dif != 0:
        s = Vec2(scroll_dif, 0)
        element.location += s
        if len(element.text) > 0:
            element.text_location += s
            if hasattr(element, "dept_text"):
                element.location_tl += s
                element.location_bl += s
                element.location_tr += s
                element.location_br += s
    element.scroll_distance = gui.scroll


class Element:
    def __init__(self, parent=None, **kwargs):
        self.size = Vec2(kwargs.get("size", (0, 0)))
        self.align = kwargs.get("align", "none")
        self.padding = Vec2(kwargs.get("padding", (0, 0)))
        self.scroll_distance = 0
        self.border = kwargs.get("border", 0)
        self.color = kwargs.get("color", (0, 0, 0))

        self.text = kwargs.get("text", "")
        self.text_align = kwargs.get("text-align", "center")
        self.text_padding = kwargs.get("text-padding", Vec2(0, 0))
        self.font = kwargs.get("font", None)
        self.text_color = kwargs.get("text-color", (0, 0, 0))

        self.handlers = kwargs.get("handlers", [])
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

    def update(self, client, gui):
        for handler in self.handlers:
            handler(self, client, gui)
        if self.get_loc()[0] > gui.resolution[0] or self.location[0] + self.size[0] < 0:
            self.visible = False
        else:
            self.visible = True

    def render(self, window):
        if self.visible:
            pygame.draw.rect(window, self.color, (*self.get_loc(), *self.size), self.border)
            if self.rendered_text is not None:
                window.blit(self.rendered_text, self.text_location.render())


class FlightElement(Element):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.dept_text = kwargs.get("dept_text", "")
        self.dept_time = kwargs.get("dept_time", "")
        self.arri_text = kwargs.get("arri_text", "")
        self.arri_time = kwargs.get("arri_time", "")
        self.side_font = kwargs.get("side_font", None)

        self.rendered_tl = self.location_tl = None
        self.rendered_bl = self.location_bl = None
        self.rendered_tr = self.location_tr = None
        self.rendered_br = self.location_br = None
        self.prep_side_text()

    def prep_side_text(self):
        self.rendered_tl = self.side_font.render(self.dept_text, 1, self.text_color)
        self.rendered_bl = self.side_font.render(self.dept_time, 1, self.text_color)
        self.rendered_tr = self.side_font.render(self.arri_text, 1, self.text_color)
        self.rendered_br = self.side_font.render(self.arri_time, 1, self.text_color)
        p_half = self.size / 2
        tl_half = Vec2(self.rendered_tl.get_rect().width, self.rendered_tl.get_rect().height) / 2
        bl_half = Vec2(self.rendered_bl.get_rect().width, self.rendered_bl.get_rect().height) / 2
        tr_half = Vec2(self.rendered_tr.get_rect().width, self.rendered_tr.get_rect().height) / 2
        br_half = Vec2(self.rendered_br.get_rect().width, self.rendered_br.get_rect().height) / 2
        self.location_tl = self.get_loc() + (p_half * Vec2(0, 1)) - (tl_half * Vec2(0, 1)) + Vec2(10, 10)
        self.location_bl = self.get_loc() + (p_half * Vec2(0, 1)) - (bl_half * Vec2(0, 1)) + Vec2(10, -10)
        self.location_tr = self.get_loc() + (p_half * Vec2(2, 1)) - (tr_half * Vec2(2, 1)) + Vec2(-10, 10)
        self.location_br = self.get_loc() + (p_half * Vec2(2, 1)) - (br_half * Vec2(2, 1)) + Vec2(-10, -10)

    def render(self, window):
        if self.visible:
            pygame.draw.rect(window, self.color, (*self.get_loc().render(), *self.size), self.border)
            window.blit(self.rendered_text, self.text_location.render())
            window.blit(self.rendered_tl, self.location_tl.render())
            window.blit(self.rendered_bl, self.location_bl.render())
            window.blit(self.rendered_tr, self.location_tr.render())
            window.blit(self.rendered_br, self.location_br.render())


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
        self.events = []
        self.scroll = 0
        self.clock = pygame.time.Clock()
        self.default_time = None

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

        for i in range(1, 35):
            if i - 1 < len(client.objects["aircraft"]):
                text = client.objects["aircraft"][i - 1].tail_number
                # drawing the flights for a given aircraft
                for flight in client.objects["flight"]:
                    if flight.aircraft.tail_number == text:
                        self.elements.append(flight.create_element(self, i))
            else:
                text = ""
            # drawing the aircraft tail number boxes
            self.elements.append(
                Element(size=Vec2(100, 35),
                        padding=Vec2(0, i * 35),
                        color=(150, 150, 150),
                        text=text,
                        font=self.font_15
                        ))
        # drawing red timeline

        self.elements.append(
            Element(
                size=Vec2(2, self.resolution[1]),
                padding=Vec2(100, 0),
                color=(255, 0, 0),
                handlers=[scroll_handler]
            )
        )
        # drawing horizontal borders
        for i in range(35):
            self.elements.append(
                Element(size=Vec2(self.resolution[0], 35),
                        padding=Vec2(0, (i - 1) * 35),
                        color=(0, 0, 0),
                        border=1,
                        ))

    def update(self, client):
        # self.clock.tick()
        # print(self.clock.get_time())
        self.window.fill(self.bg_color)
        requests = []
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                self.quit = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.scroll -= 25
                elif event.button == 5:
                    self.scroll += 25
                if self.scroll > 0:
                    self.scroll = 0

        for element in self.elements:
            element.update(client, self)
            element.render(self.window)
        pygame.display.update()
        return requests
