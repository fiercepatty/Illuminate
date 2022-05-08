import pygame

class MainMenu:

    def __init__(self, screenW, screenH):
        self.mousePos = 0
        GameTitle = "Illuminate"
        self.Height = screenH
        self.Width = screenW
        self.smolText = pygame.font.SysFont("Arial",100)
        self.smollerText = pygame.font.SysFont("Arial",75)
        self.titleText = self.smolText.render(GameTitle, True, (255,0,0))
        self.Lmid = self.titleText.get_rect().width
        self.start = self.smollerText.render("Start", True, (0, 0, 255))
        self.options = self.smollerText.render("Options", True, (0, 0, 255))
        self.quit = self.smollerText.render("Quit", True, (0, 0, 255))
        
    def draw(self, drawsurf):
        drawsurf.fill((0,0,0))
  
        drawsurf.blit(self.titleText, (125, 100))

        drawsurf.blit(self.start, (125, 250))
        drawsurf.blit(self.options, (125, 350))
        drawsurf.blit(self.quit, (125, 450))
        #pygame.draw.polygon(drawsurf, (0,255,0), ((125,250),(125,325),(285,325),(285,250)))
        #pygame.display.flip()

    def update(self, mousey):
        self.start = self.smollerText.render("Start", True, (0, 0, 255))
        self.options = self.smollerText.render("Options", True, (0, 0, 255))
        self.quit = self.smollerText.render("Quit", True, (0, 0, 255))
        
        if mousey > 250 and mousey < 350:
            self.start = self.smollerText.render("Start", True, (173,255,47))
        elif mousey > 350 and mousey < 450:
            self.options = self.smollerText.render("Options", True, (173,255,47))
        elif mousey > 450 and mousey < 550:
            self.quit = self.smollerText.render("Quit", True, (173,255,47))


    def click(self, ypos):
        if ypos > 250 and ypos < 350:
            return "Start"
        elif ypos > 350 and ypos < 450:
            return "Options"
        elif ypos > 450 and ypos < 550:
            return "Exit"
        else:
            return ""


if __name__ == "__main__":
    #test code
    

    #600 Hight
    #800 Width

    pygame.display.init()
    pygame.font.init()
    win_width = 800
    win_height = 600

    window = pygame.display.set_mode((win_width, win_height))

    menu = MainMenu(win_height, win_width, window)

    running =True

    while (running):
        cur_event = pygame.event.poll() #Event Polling
        mousey = pygame.mouse.get_pos()[1]
        if cur_event.type == pygame.QUIT: #Quit COde
            running = False
        elif cur_event.type == pygame.KEYDOWN:
            if cur_event.key == pygame.K_ESCAPE:
                running = False


        let = pygame.mouse.get_pressed()
        if (let[0] == True):
            if menu.click(mousey):
                running = False

        menu.update(mousey)

    pygame.display.quit()
