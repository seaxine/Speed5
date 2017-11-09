from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.storage.jsonstore import JsonStore
from kivy.properties import ListProperty

import random
from time import time

Builder.load_string('''
<Interface>:
	orientation: 'vertical'
<PlayButton>:
	canvas:
		Color:
			rgba: 0, 1, 0, 1
		Triangle:
			points: self.x, self.y, self.x, self.y + self.height, self.x + self.width, self.y + self.height / 2
<Root>:
	size_hint: 1, 1
	RectRoot:
		id: RectRoot
		size_hint: 1, 1
		Rect:
			text: "Red"
			text_color: 1, 0, 0, 1
			canvas:
				Color:
					rgba: self.text_color
				Rectangle:
					pos: self.pos
					size: self.size
		Rect:
			text: "Green"
			text_color: 0, 1, 0, 1
			canvas:
				Color:
					rgba: self.text_color
				Rectangle:
					pos: self.pos
					size: self.size
		Rect:
			text: "Blue"
			text_color: 0, 0, 1, 1
			canvas:
				Color:
					rgba: self.text_color
				Rectangle:
					pos: self.pos
					size: self.size
		Rect:
			text: "Yellow"
			text_color: 1, 1, 0, 1
			canvas:
				Color:
					rgba: self.text_color
				Rectangle:
					pos: self.pos
					size: self.size
		Rect:
			text: "Cyan"
			text_color: 0, 1, 1, 1
			canvas:
				Color:
					rgba: self.text_color
				Rectangle:
					pos: self.pos
					size: self.size
		Rect:
			text: "Magenta"
			text_color: 1, 0, 1, 1
			canvas:
				Color:
					rgba: self.text_color
				Rectangle:
					pos: self.pos
					size: self.size
		Rect:
			text: "White"
			text_color: 1, 1, 1, 1
			canvas:
				Color:
					rgba: self.text_color
				Rectangle:
					pos: self.pos
					size: self.size
	Label:
		id: ColorLabel
		font_size: root.height / 10
	Label:
		id: ScoreLabel
		font_size: root.height / 15
	Label:
		id: HighscoreLabel
		font_size: root.height / 15
	Label:
		id: TimerLabel
		font_size: root.height / 10
	Image:
		id: Lives
		allow_stretch: True
		height: root.height / 10
	Label:
		id: Pause
		size: root.height / 15, root.height / 10
		canvas:
			Color:
				rgba: 0.5, 0.5, 0.5, 1
			Rectangle:
				pos: self.pos
				size: self.width / 3, self.height
			Rectangle:
				pos: self.x + self.width * 2 / 3, self.y
				size: self.width / 3, self.height


	PauseScreen:
		id: PauseScreen
		size_hint: None, None
		size: root.size
		pos: root.x, root.y
		canvas:
			Color:
				rgba: 0, 0, 0, 0.75
			Rectangle:
				pos: self.pos
				size: self.size
		PlayButton:
			size: root.height / 5, root.height / 5
			pos: root.width / 2 - self.width / 2, root.height / 2 - self.height / 2
	GameOverScreen:
		id: GameOverScreen
		size_hint: None, None
		size: root.size
		pos: root.x, root.y
		canvas:
			Color:
				rgba: 0, 0, 0, 0.75
			Rectangle:
				pos: self.pos
				size: self.size
		Label:
			text: "GAME"
			color: 1, 0, 0, 1
			font_size: root.height / 3
			size: self.texture_size
			pos: root.width / 2 - self.width / 2, root.height - self.height
		Label:
			text: "OVER"
			color: 1, 0, 0, 1
			font_size: root.height / 3
			size: self.texture_size
			pos: root.width / 2 - self.width / 2, root.y
		PlayButton:
			size: root.height / 5, root.height / 5
			pos: root.width / 2 - self.width / 2, root.height / 2 - self.height / 2
	StartScreen:
		id: StartScreen
		size_hint: None, None
		size: root.size
		pos: root.x, root.y
		canvas:
			Color:
				rgba: 0, 0, 0, 1
			Rectangle:
				pos: self.pos
				size: self.size
		Label:
			id: Start5Label
			text: "5"
			color: 0.5, 0.5, 0.5, 1
			font_size: root.height / 2
			size: self.texture_size
			center: StartSpeedLabel.center
		Label:
			id: StartSpeedLabel
			text: "SPEED"
			font_size: root.height / 3
			size: self.texture_size
			pos: root.center_x - self.width / 2, root.height - Start5Label.height
		PlayButton:
			size: root.height / 5, root.height / 5
			pos: root.center_x - self.width / 2, StartSpeedLabel.y / 2
''')
class PauseScreen(Widget):
	pass
class GameOverScreen(Widget):
	pass
class StartScreen(Widget):
	pass
class PlayButton(Widget):
	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos):
			self.parent.parent.playTouch = 1
	def on_touch_up(self, touch):
		if self.collide_point(*touch.pos) and self.parent.parent.playTouch == 1:
			self.parent.parent.playTouch = 0
			self.parent.parent.startSound.play()

			if self.parent.parent.screenNum == 0:
				self.parent.parent.setup()
			self.parent.parent.screenNum = 1
			self.parent.parent.pause()


class Root(Widget):
	screenNum = 0

	dataFile = JsonStore('data.json')
	startSound = SoundLoader.load('start.wav')
	scoreSound = SoundLoader.load('point.wav')
	lifeSound = SoundLoader.load('loseLife.wav')
	gameOverSound = SoundLoader.load('gameOver.wav')

	chosen = 0
	score = 0
	if dataFile.exists('highscore'):
		highscore = dataFile.get('highscore')['value']
	else:
		highscore = 0
		dataFile.put('highscore', value = 0)
	lives = 3

	speed = 5
	timer = 5 * 60
	correctTouch = 0
	playTouch = 0
	pauseOn = 1

	def startPosSize(self, *args):
		for child in self.ids.RectRoot.children:
			if Window.height < Window.width:
				child.height = Window.height / 5
				child.width = Window.height / 5
			else:
				child.height = Window.width / 5
				child.width = Window.width / 5
			child.x = random.random() * (Window.width - child.width)
			child.y = random.random() * (Window.height - child.height)

		for child in self.ids.StartScreen.children:
			child.posBuffer = (child.x, child.y)
		for child in self.ids.PauseScreen.children:
			child.posBuffer = (child.x, child.y)
		for child in self.ids.GameOverScreen.children:
			child.posBuffer = (child.x, child.y)
	def setup(self, *args):
		idNums = range(0, len(self.ids.RectRoot.children), 1)
		for idNum, child in zip(idNums, self.ids.RectRoot.children):
			child.id = 'Rect' + str(idNum)
		self.chosen = int(random.random() * len(self.ids.RectRoot.children))
		self.startPosSize()
		self.gameClockEvent = Clock.schedule_interval(self.updatePosSize, 1/60)

	def addScore(self, *args):
		self.score += 1
		self.scoreSound.play()
		if self.score > self.highscore:
			self.highscore = self.score
			self.dataFile.put('highscore', value = self.highscore)
		self.chosen = int(random.random() * len(self.ids.RectRoot.children))
		self.timer = 5 * 60
	def loseLife(self, *args):
		self.lives -= 1
		self.lifeSound.play()
		if self.lives == 0:
			self.gameOver()
	def gameOver(self, *args):
		self.screenNum = 3
		self.gameOverSound.play()
		self.update()
		self.pause()
		self.score = 0
		self.lives = 3
		self.timer = 5 * 60
	def pause(self, *args):
		self.pauseOn *= -1
		if self.pauseOn == 1:
			self.gameClockEvent.cancel()
		if self.pauseOn == -1:
			self.gameClockEvent = Clock.schedule_interval(self.update, 1/60)
	def updatePosSize(self, *args):
		self.ids.ScoreLabel.size = self.ids.ScoreLabel.texture_size
		self.ids.ScoreLabel.center = (self.width - self.ids.Pause.width * 3 / 2 - self.ids.ScoreLabel.width, self.height - self.ids.ScoreLabel.height / 2)
		self.ids.Pause.center = (self.width - self.ids.Pause.width, self.height - self.ids.Pause.height / 2)
		self.ids.HighscoreLabel.size = self.ids.HighscoreLabel.texture_size
		self.ids.HighscoreLabel.center = (self.ids.HighscoreLabel.width, self.height - self.ids.HighscoreLabel.height / 2)
		self.ids.Lives.center = (self.center_x, self.height - self.ids.ColorLabel.height - self.ids.Lives.height / 2)
		self.ids.TimerLabel.size = self.ids.TimerLabel.texture_size
		self.ids.TimerLabel.center = (self.center_x, self.height - self.ids.ColorLabel.height - self.ids.Lives.height - self.ids.TimerLabel.height / 2)
		self.ids.ColorLabel.size = self.ids.ColorLabel.texture_size
		self.ids.ColorLabel.center = (self.center_x, self.height - self.ids.ColorLabel.height / 2)
		if self.pauseOn == 1:
			self.dispPauseScreen()
		else:
			self.hidePauseScreen()

		if self.screenNum == 0:
			self.dispStartScreen()
			self.hidePauseScreen()
			self.hideGameOverScreen()
		elif self.screenNum == 2:
			self.dispPauseScreen()
			self.hideStartScreen()
			self.hideGameOverScreen()
		elif self.screenNum == 3:
			self.dispGameOverScreen()
			self.hideStartScreen()
			self.hidePauseScreen()
		else:
			self.hideStartScreen()
			self.hidePauseScreen()
			self.hideGameOverScreen()

	def update(self, *args):
		self.timer -= 1
		self.speed = (self.score / 5) + 5
		self.ids.ScoreLabel.text = str(self.score)
		self.ids.HighscoreLabel.text = str(self.highscore)
		self.ids.Lives.source = 'Lives' + str(self.lives) + '.png'
		self.ids.TimerLabel.text = str(int((self.timer / 60) + 1))
		for child in self.ids.RectRoot.children:
			child.x += self.speed * child.velocity[0]
			child.y += self.speed * child.velocity[1]

			if child.x < 0 or (child.x + child.width) > Window.width:
				child.velocity[0] *= -1
			if child.y < 0 or (child.y + child.height) > Window.height:
				child.velocity[1] *= -1

			if child.id == 'Rect' + str(self.chosen):
				self.ids.ColorLabel.text = child.text
				self.ids.ColorLabel.color = child.text_color
		if self.timer == 0:
			self.gameOver()

	def dispStartScreen(self, *args):
		self.ids.StartScreen.pos = (self.pos)
		for child in self.ids.StartScreen.children:
			child.pos = (child.posBuffer[0], child.posBuffer[1])
	def hideStartScreen(self, *args):
		self.ids.StartScreen.pos = (self.ids.StartScreen.x, self.ids.StartScreen.y + self.height)
		for child in self.ids.StartScreen.children:
			child.pos = (child.posBuffer[0], child.posBuffer[1] + self.height)
	def dispPauseScreen(self, *args):
		self.ids.PauseScreen.pos = (self.pos)
		for child in self.ids.PauseScreen.children:
			child.pos = (child.posBuffer[0], child.posBuffer[1])
	def hidePauseScreen(self, *args):
		self.ids.PauseScreen.pos = (self.ids.PauseScreen.x, self.ids.PauseScreen.y + self.height)
		for child in self.ids.PauseScreen.children:
			child.pos = (child.posBuffer[0], child.posBuffer[1] + self.height)
	def dispGameOverScreen(self, *args):
		self.ids.GameOverScreen.pos = (self.pos)
		for child in self.ids.GameOverScreen.children:
			child.pos = (child.posBuffer[0], child.posBuffer[1])
	def hideGameOverScreen(self, *args):
		self.ids.GameOverScreen.pos = (self.ids.GameOverScreen.x, self.ids.GameOverScreen.y + self.height)
		for child in self.ids.GameOverScreen.children:
			child.pos = (child.posBuffer[0], child.posBuffer[1] + self.height)

	def on_pos(self, *args):
		self.startPosSize()
	def on_size(self, *args):
		self.startPosSize()

class RectRoot(Widget):
	pass
class Rect(Widget):
	velocity = ListProperty([0, 0])

	def __init__(self, **kwargs):
		super(Rect, self).__init__(**kwargs)
		self.velocity[0] = (int((random.random() + 0.5)) - 0.5) * 2
		self.velocity[1] = (int((random.random() + 0.5)) - 0.5) * 2

	def on_touch_down(self, touch):
		if self.parent.parent.ids.Pause.collide_point(*touch.pos) and self.parent.parent.screenNum == 1:
			self.parent.parent.correctTouch = 1
			self.parent.parent.screenNum = 2
			self.parent.parent.pause()
		if self.parent.parent.pauseOn == -1:
			if self.collide_point(*touch.pos) and str(self.id) == 'Rect' + str(self.parent.parent.chosen):
				self.parent.parent.correctTouch = 1
				self.parent.parent.addScore()
			if str(self.id) != 'Rect' + str(len(self.parent.parent.ids.RectRoot.children) - 1) or self.parent.parent.correctTouch == 1:
				pass
			else:
				self.parent.parent.loseLife()
	def on_touch_up(self, touch):
		self.parent.parent.correctTouch = 0
class Speed5App(App):

	def build(self):
		return Root()

if __name__ == "__main__":
	Speed5App().run()