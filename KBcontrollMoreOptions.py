# TCP connection with Labview VI
# import the necessary packages
import numpy as np
import pygame
import socket
import struct
import time

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 8089))
server.listen(1)
print("Server Running")
conn, addr = server.accept()
print("Client Connected")

pygame.init()

display_width = 300
display_height = 300

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('DroneMove')
clock = pygame.time.Clock()

crashed = False
dataToSend = 0
otherEvent = False
stringToSend = ' '


while not crashed:


	#cmnd = conn.recv(1) #Default command packet



	#Python controll part
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			crashed = True

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				print("Forward")
				dataToSend |= (1<<3)


			if event.key == pygame.K_DOWN:
				print("Backward")
				dataToSend |= (1<<1)

			if event.key == pygame.K_LEFT:
				print("Left")
				dataToSend |= (1<<2)

			if event.key == pygame.K_RIGHT:
				print("Right")
				dataToSend |= (1<<0)

			if event.key == pygame.K_w:
				print("Up")
				dataToSend |= (1<<7)

			if event.key == pygame.K_s:
				print("Down")
				dataToSend |= (1<<5)

			if event.key == pygame.K_a:
				print("Yaw Left")
				dataToSend |= (1<<6)

			if event.key == pygame.K_d:
				print("Yaw Right")
				dataToSend |= (1<<4)

			if event.key == pygame.K_SPACE:
				print("StartPhoto")
				stringToSend = 'Phto'
				otherEvent = True



		if event.type == pygame.KEYUP:
			if event.key == pygame.K_UP:
				print("-Forward")
				dataToSend &= (~(1<<3))


			if event.key == pygame.K_DOWN:
				print("-Backward")
				dataToSend &= (~(1<<1))


			if event.key == pygame.K_LEFT:
				print("-Left")
				dataToSend &= (~(1<<2))


			if event.key == pygame.K_RIGHT:
				print("-Right")
				dataToSend &= (~(1<<0))


			if event.key == pygame.K_w:
				print("-Up")
				dataToSend &= (~(1<<7))


			if event.key == pygame.K_s:
				print("-Down")
				dataToSend &= (~(1<<5))


			if event.key == pygame.K_a:
				print("-Yaw Left")
				dataToSend &= (~(1<<6))


			if event.key == pygame.K_d:
				print("-Yaw Right")
				dataToSend &= (~(1<<4))


	if otherEvent:
		conn.sendall(stringToSend.encode('utf-8'))
		time.sleep(0.1)
		otherEvent = False
	else:
		print(dataToSend)

		packedData = struct.pack("B", dataToSend)
		conn.sendall(b'Move')
		conn.sendall(packedData)
		time.sleep(0.1)

	gameDisplay.fill(white)
	pygame.display.update()
	clock.tick(60)


server.close()
pygame.quit()
quit()
