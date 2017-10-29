# import the necessary packages
import numpy as np
import pygame
import threading


pygame.init()

display_width = 800
display_height = 600

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('DroneMove')
clock = pygame.time.Clock()

crashed = False
dataToSend = ' '

while not crashed:


	#Python controll part
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			crashed = True

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				print("Forward")

			if event.key == pygame.K_DOWN:
				print("Backward")

			if event.key == pygame.K_LEFT:
				print("Left")

			if event.key == pygame.K_RIGHT:
				print("Right")

			if event.key == pygame.K_w:
				print("Up")

			if event.key == pygame.K_s:
				print("Down")

			if event.key == pygame.K_a:
				print("Yaw Left")

			if event.key == pygame.K_d:
				print("Yaw Right")

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_UP:
				print("-Forward")

			if event.key == pygame.K_DOWN:
				print("-Backward")

			if event.key == pygame.K_LEFT:
				print("-Left")

			if event.key == pygame.K_RIGHT:
				print("-Right")

			if event.key == pygame.K_w:
				print("-Up")

			if event.key == pygame.K_s:
				print("-Down")

			if event.key == pygame.K_a:
				print("-Yaw Left")

			if event.key == pygame.K_d:
				print("-Yaw Right")



	gameDisplay.fill(white)
	pygame.display.update()
	clock.tick(60)


pygame.quit()
quit()
