import pygame
import sys

class Button:
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        if self.text != '':
            font = pygame.font.SysFont('comicsans', 60)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False

def redrawWindow(win, button):
    win.fill((255,255,255))
    button.draw(win, (0,0,0))

def main():
    pygame.init()
    run = True
    win = pygame.display.set_mode((500,500))
    clock = pygame.time.Clock()
    button = Button((0,255,0), 150, 225, 250, 100, 'text')

    while run:
        redrawWindow(win, button)
        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.isOver(pos):
                    print('clicked the button')
            if event.type == pygame.MOUSEMOTION:
                if button.isOver(pos):
                    button.color = (255,0,0)
                else:
                    button.color = (0,255,0)

main()
