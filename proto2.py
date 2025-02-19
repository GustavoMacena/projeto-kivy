from kivy.uix.accordion import StringProperty
from kivy.uix.actionbar import partial
from kivy.uix.accordion import NumericProperty
import kivy
from kivy.app import App 
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image, AsyncImage
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from kivy.animation import Animation
from random import random
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
from kivy.core.image import Image as CoreImage

Window.size = (1280, 720) 
Window.minimum_width, Window.minimum_height = (1280, 720)

class Manager(ScreenManager):
    pass

class Menu(Screen):
    pass

class Game(Screen):
    obstacles = []
    score = NumericProperty(0)
    highscore = NumericProperty(0)
    alive = True

    def on_enter(self, *args):
        with open("assets/highscore.txt", "r") as f:
            self.highscore = int(f.read())
        Clock.schedule_interval(self.update, 1/30)
        Clock.schedule_interval(self.putObstacle, 1) 

    def on_pre_enter(self, *args):
        self.ids.player.y = self.height/2
        self.ids.player.speed=0
        self.score = 0
    
    def update(self, *args):
        self.ids.player.speed += -self.height *2* 1/30
        self.ids.player.y += self.ids.player.speed * 1/30
        if self.ids.player.y > self.height or self.ids.player.y < 0:
            self.alive = False
        elif self.playerCollided():
            self.alive = False
        if not self.alive :
            if self.score > self.highscore :
                self.highscore = self.score
                with open("assets/highscore.txt", "w") as f:
                    f.write(str(self.highscore))
            self.alive = True
            self.gameover()

    def putObstacle(self, *args):
        gap = self.height*0.4
        position = (self.height - gap)*random()
        width = self.width*0.07

        obstacleLow = Obstacle(x=self.width, height= position, width = width)
        obstacleHigh = Obstacle(x=self.width, y = position + gap, height= self.height - position - gap, width = width)
        self.add_widget(obstacleLow)
        self.add_widget(obstacleHigh)
        self.obstacles.append(obstacleLow)
        self.obstacles.append(obstacleHigh)

    def collision(self, wid1, wid2):
        if wid2.x <= wid1.x + wid1.width and \
           wid2.x + wid2.width > wid1.x and \
           wid2.y <= wid1.y + wid1.height and \
           wid2.y + wid2.height > wid1.y:
            return True
        else:
            return False
        
    def playerCollided(self):
        collided = False
        for obstacle in self.obstacles:
            if self.collision(self.ids.player, obstacle):
                collided = True
                break
        return collided

    def gameover(self, *args):
        Clock.unschedule(self.update, 1/30)
        Clock.unschedule(self.putObstacle, 1)
        for ob in self.obstacles:
            ob.anim.cancel(ob)
            self.remove_widget(ob)
            self.obstacles = []
        App.get_running_app().root.current = 'gameover'
    
    def on_touch_down(self, touch):
        self.ids.player.speed += self.height*0.7

class Obstacle(Widget):
    scored = False
    gameScreen = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anim = Animation(x=-self.width, duration=3)
        self.anim.bind(on_complete=self.vanish)
        self.anim.start(self)
        self.gameScreen = App.get_running_app().root.get_screen('Game')

        self.texture = CoreImage("assets/building.png").texture
        self.texture.wrap = 'repeat'

        self.bind(pos=self.update_rectangle, size=self.update_rectangle)

        with self.canvas:
            Color(1, 1, 1)
            self.rect = Rectangle(texture=self.texture, pos=self.pos, size=self.size)

    def update_rectangle(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

        tex_width = self.texture.width
        tex_height = self.texture.height

        scale_x = self.width / tex_width

        repeat_y = self.height / tex_height

        self.rect.tex_coords = (
            0, 0,
            scale_x, 0,
            scale_x, repeat_y, 
            0, repeat_y, 
        )

    def on_x(self, *args):
        if self.gameScreen :
            if self.x < self.gameScreen.ids.player.x and not self.scored:
                self.gameScreen.score += 5
                self.scored = True

    def vanish(self,*args):
        self.gameScreen.remove_widget(self)
        self.gameScreen.obstacles.remove(self)
        
class GameOver(Screen):
    pass

class ChoosePlayer(Screen):
    currentplayer = StringProperty('assets/players/ratue_pixel_art.png')
    cicerue = False
    matue = False
    davibritue = False
    playerlist = ['Ratuê', 'Ciceruê', 'Matuê', 'Davi Brituê']
    playerlistImage = ['assets/players/ratue_pixel_art.png', 'assets/players/cicero.png', 'assets/players/matue_pixel_art.png', 'assets/players/davi_brito.png']
    count = NumericProperty(0)

    with open("assets/highscore.txt", "r") as f:
        highscore = int(f.read())
        if highscore >= 200 :
            cicerue = True
        if highscore >= 420 :
            matue = True
        if highscore >= 1000 :
            davibritue = True
    
    def ChangePlayerRight(self):
        self.count = (self.count + 1) % len(self.playerlistImage)
        self.currentplayer = self.playerlistImage[self.count]
        App.get_running_app().current_player_image = self.currentplayer
    
    def ChangePlayerLeft(self):
        self.count = (self.count - 1) % len(self.playerlistImage)
        self.currentplayer = self.playerlistImage[self.count]
        App.get_running_app().current_player_image = self.currentplayer

class Player(Image):
    speed = NumericProperty(0)

class Ratue(App):
    current_player_image = StringProperty('assets/players/ratue_pixel_art.png')

Ratue().run()