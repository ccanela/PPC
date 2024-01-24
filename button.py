import pygame

class Button:
    def __init__(self, x, y, image, scale, id, text=''):
        self.image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.id = id
        self.text = text

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action
image = pygame.image.load().convert_alpha 
button1 = Button(50, 50, image, 1, 'button1')
button2 = Button(50, 80, )
if button1.draw(screen):
    print('Button1 was clicked!')

