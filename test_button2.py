import pygame

class Button:
    def __init__(self, image, position, action=None, scale=1.0, value=None):
        self.original_image = pygame.image.load(image)
        self.scale = scale
        self.image = self.scale_image(self.original_image, scale)
        self.position = position
        self.rect = self.image.get_rect(topleft=position)
        self.hovered = False
        self.action = action
        self.value = value

    def scale_image(self, image, scale):
        infoObject = pygame.display.Info()
        screen_width = infoObject.current_w
        screen_height = infoObject.current_h

        image_width = int(screen_width * scale)
        image_height = int(image.get_height() * image_width / image.get_width())
        return pygame.transform.scale(image, (image_width, image_height))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if not self.hovered:
                    self.hovered = True
                    self.image = self.scale_image(self.original_image, self.scale*1.05)
                    self.rect = self.image.get_rect(center=self.rect.center)
            else:
                if self.hovered:
                    self.hovered = False
                    self.image = self.scale_image(self.original_image, self.scale)
                    self.rect = self.image.get_rect(topleft=self.position)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                print("Button clicked!")
                if self.action: 
                    self.action()
class Text:
    def __init__(self, text, position, font_name=None, font_size=50, color=(0, 0, 0), box_color=None, box_padding=10):
        self.font = pygame.font.Font(font_name, font_size)
        self.text_surface = self.font.render(text, True, color)
        self.text_rect = self.text_surface.get_rect(topleft=position)

        if box_color:
            self.box_color = box_color
            self.box_padding = box_padding
            self.box_rect = pygame.Rect(
                self.text_rect.x - box_padding,
                self.text_rect.y - box_padding,
                self.text_rect.width + 2 * box_padding,
                self.text_rect.height + 2 * box_padding
            )

    def draw(self, screen):
        if hasattr(self, 'box_color'):
            pygame.draw.rect(screen, self.box_color, self.box_rect)
        screen.blit(self.text_surface, self.text_rect)


def hello():
    print("Hello")


players_cards = {'player1': [{'color': 'white', 'number': 5}, {'color': 'yellow', 'number': 2}, {'color': 'blue', 'number': 4}, {'color': 'blue', 'number': 5}, {'color': 'yellow', 'number': 2}], 'player2': [{'color': 'green', 'number': 2}, {'color': 'green', 'number': 1}, {'color': 'green', 'number': 2}, {'color': 'blue', 'number': 1}, {'color': 'green', 'number': 1}], 'player3': [{'color': 'red', 'number': 2}, {'color': 'yellow', 'number': 4}, {'color': 'yellow', 'number': 3}, {'color': 'green', 'number': 5}, {'color': 'yellow', 'number': 1}], 'player4': [{'color': 'white', 'number': 4}, {'color': 'blue', 'number': 3}, {'color': 'red', 'number': 1}, {'color': 'green', 'number': 3}, {'color': 'green', 'number': 4}], 'player5': [{'color': 'red', 'number': 4}, {'color': 'blue', 'number': 3}, {'color': 'red', 'number': 5}, {'color': 'white', 'number': 2}, {'color': 'yellow', 'number': 5}]}
pygame.init()
pygame.font.init()
text = Text("HANABI GAME", (250, 300), font_size=50, box_color=(255, 255, 255), box_padding=20)
screen = pygame.display.set_mode((800, 600))
buttons = []
for i, card in enumerate(players_cards["player2"]): 
    button = Button(f'{card["number"]}_{card["color"]}.png', (100 + i*65, 100), action=hello, scale=0.1, value=(card["number"], card["color"])) 
    buttons.append(button)
    

running = True
while running:
    screen.fill((200, 255, 255))
    for button in buttons:
        button.draw(screen)
    text.draw(screen)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for button in buttons:
            button.handle_event(event)
    

pygame.quit()

""" pygame.init()
screen = pygame.display.set_mode((800, 600))
button1 = Button('5_green.png', (100, 100), scale=0.1) 
button2 = Button('4_blue.png', (100, 200), scale=0.1) 

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        button1.handle_event(event)
        button2.handle_event(event)

    screen.fill((200, 255, 255))
    button1.draw(screen)
    button2.draw(screen)
    pygame.display.flip()

pygame.quit()
 """
