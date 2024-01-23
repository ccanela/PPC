import pygame

class Button:
    def __init__(self, image, position, scale=1.0):
        self.original_image = pygame.image.load(image)
        self.scale_image(scale)
        self.position = position
        self.rect = self.image.get_rect(topleft=position)
        self.hovered = False

    def scale_image(self, scale):
        width, height = self.original_image.get_size()
        self.image = pygame.transform.scale(self.original_image, (int(width*scale), int(height*scale)))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if not self.hovered:
                    self.hovered = True
                    self.scale_image(1.1)
                    self.rect = self.image.get_rect(center=self.rect.center)
            else:
                if self.hovered:
                    self.hovered = False
                    self.scale_image(1.000005)
                    self.rect = self.image.get_rect(topleft=self.position)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                print("Button clicked!")

# Uso de la clase Button
pygame.init()
screen = pygame.display.set_mode((800, 600))
button = Button('1_green.png', (100, 100), scale=0.2)  # Cambia el valor de scale según sea necesario

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        button.handle_event(event)

    screen.fill((255, 255, 255))
    button.draw(screen)
    pygame.display.flip()

pygame.quit()

