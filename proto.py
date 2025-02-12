from kivy.uix.actionbar import partial
from kivy.uix.accordion import NumericProperty
import kivy
from kivy.app import App 
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from kivy.animation import Animation
from random import random
from kivy.core.window import Window

Window.size = (1280, 720) 
Window.minimum_width, Window.minimum_height = (1280, 720)

class Manager(ScreenManager):
    pass

class Menu(Screen):
    pass

class Game(Screen):
    obstacles = []
    score = NumericProperty(0)
    f = open("assets/highscore.txt", "r+")
    highscore = NumericProperty(int(f.read()))

    def on_enter(self, *args):
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
            if self.score > self.highscore :
                self.highscore = self.score
                print(self.f.write(str(self.highscore)))
            self.gameover()
        elif self.playerCollided():
            if self.score > self.highscore :
                self.highscore = self.score
                print(self.f.write(str(self.highscore)))
            self.gameover()            


    def putObstacle(self, *args):
        gap = self.height*0.4
        position = (self.height - gap)*random()
        width = self.width*0.05

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

class Player(Image):
    speed = NumericProperty(0)

class Ratue(App):
    pass

Ratue().run()