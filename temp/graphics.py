"""
AirSchedule Graphics
2020

This file includes the GUI and the elements that it is built out of
"""
import pygame
from vec2 import Vec2
import time
from datetime import timedelta


# Checks to see if a point is inside an element
def inside(element, po, split=False):
    # "Split" enables returning separate booleans for vertical and horizontal containment
    tl = element.location
    br = element.location + element.size
    if tl[0] < po[0] < br[0] and tl[1] < po[1] < br[1]:
        if split:
            return True, True
        return True
    if split:
        return tl[0] < po[0] < br[0], tl[1] < po[1] < br[1]
    return False


# A handler that causes an element to scroll horizontally depending on a value inside the GUI
def scroll_handler(element, client, gui):
    element.loc_mod += Vec2(gui.scroll, 0)


# A handler that updates the position of the red timeline
def time_handler(element, client, gui):
    element.loc_mod += Vec2(((client.time - gui.default_time).total_seconds() / 60) * client.MINUTES_WIDTH, 0)


# A handler that determines whether or not an element has been selected or deselected
# Deselection is used to spawn event requests that are sent back to the server
def selection_handler(element, client, gui):
    if gui.click and inside(element, gui.mouse_start) and element.object.status == "scheduled":
        element.selected = True
    elif gui.double_click and inside(element, gui.mouse_start, split=True)[1]:
        # Select a whole row when double-clicked
        if (element.location + element.size)[0] > gui.mouse_start[0] and element.object.status == "scheduled":
            element.selected = True
    if (not gui.click and not gui.double_click) or element.object.status != "scheduled":
        if element.selected:
            element.deselected = True
        else:
            element.deselected = False
        element.selected = False


# Handler that allows flights to be dragged around the schedule, provided that they haven't departed yet
# Snaps the element to an aircraft and in increments of 5 minutes
def drag_handler(element, client, gui):
    # how far the mouse has moved
    drag = gui.mouse_pos - gui.mouse_start
    # ac_change keeps track of how many rows we have dragged the flight through
    # we also make sure that the user can't drag the flight to an empty row (No aircraft)
    flight = element.object
    ac_list = client.objects["aircraft"]
    ac_index = ac_list.index(element.object.aircraft)
    lower_limit = 0 - ac_index
    upper_limit = len(ac_list) - ac_index - 1
    ac_change = drag[1] // 35
    if ac_change < lower_limit:
        ac_change = lower_limit
    elif ac_change > upper_limit:
        ac_change = upper_limit
    # how much time we have passed
    time_change = drag[0] // (client.MINUTES_WIDTH*5)
    # modifies the loc_mod of the selected flight(s) so that we can see them being dragged around
    if element.selected:
        element.loc_mod += Vec2(time_change * client.MINUTES_WIDTH * 5, ac_change*35)

    # If the element is moved and deselected we create an event request to send to the server
    if element.deselected:
        if ac_change != 0:
            old_ac_name = flight.aircraft.name
            new_ac_name = ac_list[ac_index + ac_change].name
            client.new_events.append("flight,%s,aircraft,%s,%s" % (flight.name, old_ac_name, new_ac_name))
        if time_change != 0:
            old_dp = flight.dept_time.isoformat()
            old_ar = flight.arri_time.isoformat()
            new_dp = (flight.dept_time + timedelta(minutes=time_change*5)).isoformat()
            new_ar = (flight.arri_time + timedelta(minutes=time_change*5)).isoformat()
            client.new_events.append("flight,%s,dept_time,%s,%s" % (flight.name, old_dp, new_dp))
            client.new_events.append("flight,%s,arri_time,%s,%s" % (flight.name, old_ar, new_ar))


# Building block of the gui
class Element:
    def __init__(self, parent=None, **kwargs):
        self.size = Vec2(kwargs.get("size", (0, 0)))
        # how the element is aligned in comparison to its parent. supports center, left, top, etc
        self.align = kwargs.get("align", "none")
        self.padding = Vec2(kwargs.get("padding", (0, 0)))
        # thickness of the element's border. 0 for no border
        self.border = kwargs.get("border", 0)
        self.border_color = kwargs.get("border_color", (0, 0, 0))
        # whether or not to render a background to this element
        self.only_border = kwargs.get("only_border", False)
        self.color = kwargs.get("color", (0, 0, 0))
        # used to move an element from its default location temporarily
        self.loc_mod = Vec2(0, 0)

        # Text to display on the element
        self.text = kwargs.get("text", "")
        self.text_align = kwargs.get("text-align", "center")
        self.text_padding = kwargs.get("text-padding", Vec2(0, 0))
        self.font = kwargs.get("font", None)
        self.text_color = kwargs.get("text-color", (0, 0, 0))

        # List of handler functions
        self.handlers = kwargs.get("handlers", [])
        # Whether or not the element should render
        self.visible = kwargs.get("visible", True)

        # If the element has a parent
        self.parent = parent

        # Setting a default size depending on whether or not there's a parent element
        if self.size == (0, 0):
            if self.parent is not None:
                self.size = self.parent.size
            else:
                self.size = Vec2(1920, 1050)

        # Locations are created once, and modified as necessary by self.loc_mod when rendering
        self.location = None
        # Same with text
        self.rendered_text, self.text_location = self.prep_text()

        # Whether or not the element has been selected or deselected
        self.selected = False
        self.deselected = False

    # finds the location of this element, taking into consideration its alignment/padding/loc_mod/etc
    def get_loc(self):
        if self.location is None:
            if self.parent is None:
                self.location = self.padding.copy() + self.loc_mod
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
                self.location = p_loc + align + self.padding + self.loc_mod
        return self.location + self.loc_mod

    # finds the location of the element's text, and renders it to a surface so that we can reuse the surface
    # because rendering text in pygame is expensive
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

    # calls all of the handlers if there are any, and determines if this element is onscreen
    # if it's offscreen we make it invisible
    def update(self, client, gui):
        self.loc_mod = 0
        for handler in self.handlers:
            handler(self, client, gui)
        if self.get_loc()[0] > gui.resolution[0] or self.location[0] + self.size[0] < 0:
            self.visible = False
        else:
            self.visible = True

    # renders the element
    def render(self, window):
        if self.visible:
            if not self.only_border:
                pygame.draw.rect(window, self.color, (*self.get_loc(), *self.size), 0)
            if self.border > 0:
                pygame.draw.rect(window, self.border_color, (*self.get_loc(), *self.size), self.border)
            if self.rendered_text is not None:
                window.blit(self.rendered_text, self.text_location.render())


# A flight element is an extension of Element that has extra text for the dept/arri times and locations
class FlightElement(Element):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.object = kwargs.get("object", None)
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
            pygame.draw.rect(window, self.color, (*self.get_loc().render(), *self.size), 0)
            window.blit(self.rendered_text, (self.text_location + self.loc_mod).render())
            window.blit(self.rendered_tl, (self.location_tl + self.loc_mod).render())
            window.blit(self.rendered_bl, (self.location_bl + self.loc_mod).render())
            window.blit(self.rendered_tr, (self.location_tr + self.loc_mod).render())
            window.blit(self.rendered_br, (self.location_br + self.loc_mod).render())
            if self.selected:
                pygame.draw.rect(window, self.border_color, (*self.get_loc(), *self.size), self.border)


# The GUI is how you interact and view the client.
class Gui:
    def __init__(self):
        # Prepping pygame and the gui window
        pygame.init()
        pygame.font.init()
        self.resolution = (1920, 1050)
        self.window = pygame.display.set_mode(self.resolution, pygame.RESIZABLE)
        pygame.display.set_caption("AirSchedule")
        pygame.display.set_icon(pygame.image.load("icon.png"))
        self.bg_color = (100, 100, 100)

        # Loading up some commonly used fonts
        self.font_15 = pygame.font.SysFont("courier", 15)
        self.font_25 = pygame.font.SysFont("courier", 25)
        self.font_30 = pygame.font.SysFont("courier", 30)

        self.quit = False
        # The elements currently active
        self.elements = []
        # Pygame events
        self.events = []
        self.scroll = 0
        self.clock = pygame.time.Clock()
        # The reference time that everything is referenced to
        self.default_time = None

        # Mouse activity
        self.click = False
        self.click_time = time.time()
        self.double_click = False
        self.mouse_start = Vec2(0, 0)
        self.mouse_pos = Vec2(0, 0)

    # The following few functions replace self.elements with whatever they need to construct the desired view
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

    # main page
    def schedule_page(self, client):
        self.elements = []
        # Creating all the aircraft elements, and all the flight elements for each aircraft
        # Populates an entire column with aircraft elements, but leaves extras blank
        for i in range(35):
            if i < len(client.objects["aircraft"]):
                text = client.objects["aircraft"][i].tail_number
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
                handlers=[scroll_handler, time_handler]
            )
        )
        # drawing horizontal borders
        for i in range(35):
            self.elements.append(
                Element(size=Vec2(self.resolution[0], 35),
                        padding=Vec2(0, (i - 1) * 35),
                        color=(0, 0, 0),
                        border=1,
                        only_border=True
                        ))

    # Causes the gui to update all of its events, elements, and render
    def update(self, client):
        # self.clock.tick()
        # print(self.clock.get_time())
        self.window.fill(self.bg_color)
        # Refreshing pygame and getting mouse/key events
        self.events = pygame.event.get()
        self.mouse_pos = Vec2(pygame.mouse.get_pos())
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
                if event.button == 1:
                    if time.time() - self.click_time < 0.25:
                        self.click = False
                        self.double_click = True
                        self.mouse_start = self.mouse_pos.copy()
                    else:
                        self.click = True
                        self.click_time = time.time()
                        self.mouse_start = self.mouse_pos.copy()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.click = self.double_click = False
        # Update and render elements
        for element in self.elements:
            element.update(client, self)
            element.render(self.window)
        # update display
        pygame.display.update()
