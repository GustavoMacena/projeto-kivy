from kivy.uix.accordion import StringProperty
from kivy.uix.actionbar import partial
from kivy.uix.accordion import NumericProperty
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
    """ 
    Argumento do arquivo kv que dá o nome para as telas.
    """

class Menu(Screen):
    pass
    """
    Tela inicial do jogo. Nela temos 3 botões (2 atribuidos à 2 telas novas e um que fecha a aplicação), o layout principal que o jogo se passa e a logo.
    """

class Game(Screen):
    """
    Tela principal do jogo. Nela temos o Player, os Obstáculos, o Score e o layout de fundo.
    """
    obstacles = []
    score = NumericProperty(0)
    highscore = NumericProperty(0)
    alive = True

    def on_enter(self, *args):
        # Função que dita o necessário para o funcionamento do jogo ao entrar (highscore e ticks).
        with open("assets/highscore.txt", "r") as f: 
            self.highscore = int(f.read())
        Clock.schedule_interval(self.update, 1/30)
        Clock.schedule_interval(self.putObstacle, 1) 

    def on_pre_enter(self, *args):
        # Função que seta as configurações necessárias antes de iniciar a tela de jogo.(Altura e velocidade do Player, Score inicial)
        self.ids.player.y = self.height/2
        self.ids.player.speed=0
        self.score = 0
    
    def update(self, *args):
        # Função que usa o clock como guia para atualizar a queda do player e checar se foi atingido por um obstáculo (caso tenha sido, atualiza o highscore e chama a função gameover)
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
        # Função que adiciona os obstáculos na tela Game, ela cria o obstáculo em cima e embaixo deixando um espaço de posição aleatória entre eles.
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
        # Função que usa a técnica AABB para checagem de colisões.
        if wid2.x <= wid1.x + wid1.width and \
           wid2.x + wid2.width > wid1.x and \
           wid2.y <= wid1.y + wid1.height and \
           wid2.y + wid2.height > wid1.y:
            return True
        else:
            return False
        
    def playerCollided(self):
        # Função que checa a função collision em cada obstáculo.
        collided = False
        for obstacle in self.obstacles:
            if self.collision(self.ids.player, obstacle):
                collided = True
                break
        return collided

    def gameover(self, *args):
        # Função que chama a tela de Game Over caso haja uma colisão, ela também zera lista de obstáculos e para a produção deles.
        Clock.unschedule(self.update, 1/30)
        Clock.unschedule(self.putObstacle, 1)
        for ob in self.obstacles:
            ob.anim.cancel(ob)
            self.remove_widget(ob)
            self.obstacles = []

        gameover_screen = App.get_running_app().root.get_screen('gameover')
        gameover_screen.score = self.score
        App.get_running_app().root.current = 'gameover'
    
    def on_touch_down(self, touch):
        # Função que aumenta a velocidade do player ao clicar.
        self.ids.player.speed += self.height*0.7

class Obstacle(Widget):
    """
    Objeto obstáculo, responsável pela criação, animação e destruição do obstáculo na tela Game.
    """
    scored = False
    gameScreen = None

    def __init__(self, **kwargs):
        # Função que gera o widget Retângulo e o faz percorrer a tela ao longo de 3 segundos, dá a textura de prédio.
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
        # Função que adapta a textura do obstáculo indiferente de sua altura, repetindo a textura ao longo do eixo y.
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
        # Função que pontua o usuário sempre que passa por um obstáculo.
        if self.gameScreen :
            if self.x < self.gameScreen.ids.player.x and not self.scored:
                self.gameScreen.score += 5
                self.scored = True

    def vanish(self,*args):
        # Função que remove os obstáculos da tela.
        self.gameScreen.remove_widget(self)
        self.gameScreen.obstacles.remove(self)
        
class GameOver(Screen):
    """
    Tela de Game Over. Nela temos 2 botões atribuidos a duas telas diferentes (Game e Menu), o layout de fundo e um texto mostando a pontuação que foi feita juntamente com a confirmação visual que o jogador perdeu.
    """
    score = NumericProperty(0)

class ChoosePlayer(Screen):
    """
    Tela de Seleção de personagem. Tela com 3 botões (2 para selecionar o personagem no formato de carrossel e 1 para jogar com o personagem selecionado), 3 Labels (um estático de "Escolha seu personagem", outro que muda de acordo com o personagem sendo mostrado, outro que aparece apenas quando o usuário não possui a pontuação mínima necessária para jogar com o personagem seleciodo) e uma imagem do personagem selecionado.
    """
    currentplayer = StringProperty('assets/players/ratue_pixel_art.png')
    cicerue = False
    matue = False
    davibritue = False
    playerlist = ['Ratuê','Davi Brituê' , 'Matuê', 'Ciceruê']
    playerlistImage = [
        'assets/players/ratue_pixel_art.png',
        'assets/players/davi_brito.png',
        'assets/players/matue_pixel_art.png',
        'assets/players/cicero.png'
    ]
    count = NumericProperty(0)
    message = StringProperty('')

    def CheckHighscore(self, player):
        # Função que checa se o usuário tem a pontuação mínima necessária para escolher o personagem.
        with open("assets/highscore.txt", "r") as f:
            highscore = int(f.read())
            if highscore >= 200:
                self.davibritue = True
            if highscore >= 420:
                self.matue = True
            if highscore >= 1000:
                self.cicerue = True

        if player == 'Davi Brituê' and not self.davibritue:
            self.message = "Você precisa do highscore de 200 para desbloquear o Davi Brituê!"
            return False
        if player == 'Matuê' and not self.matue:
            self.message = "Você precisa do highscore de 420 para desbloquear o Matuê!"
            return False
        if player == 'Ciceruê' and not self.cicerue:
            self.message = "Você precisa do highscore de 1000 para desbloquear o Ciceruê!"
            return False
        return True

    def ChangePlayerRight(self):
        # Função que roda o carrossel de escolha de personagens para a direita.
        next_player_index = (self.count + 1) % len(self.playerlistImage)
        next_player = self.playerlist[next_player_index]

        if not self.CheckHighscore(next_player):
            return 

        self.count = next_player_index
        self.currentplayer = self.playerlistImage[self.count]
        App.get_running_app().current_player_image = self.currentplayer
        self.message = ''

    def ChangePlayerLeft(self):
        # Função que roda o carrossel de escolha de personagens para esquerda.
        previous_player_index = (self.count - 1) % len(self.playerlistImage)
        previous_player = self.playerlist[previous_player_index]

        if not self.CheckHighscore(previous_player):
            return

        self.count = previous_player_index
        self.currentplayer = self.playerlistImage[self.count]
        App.get_running_app().current_player_image = self.currentplayer
        self.message = ''

class Player(Image):
    speed = NumericProperty(0)

class Ratue(App):
    current_player_image = StringProperty('assets/players/ratue_pixel_art.png')

Ratue().run()