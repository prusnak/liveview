#!/usr/bin/python2

import bluetooth
import LiveViewMessages
import sys
import time
import struct


menuVibrationTime = 5
is24HourClock = True


testPngFd = open("test36.png")
testPng = testPngFd.read()
testPngFd.close()

testPngFd = open("test128.png")
testPng128 = testPngFd.read()
testPngFd.close()





serverSocket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
serverSocket.bind(("",1))
serverSocket.listen(1)

bluetooth.advertise_service(serverSocket, "LiveView", 
			    service_classes=[ bluetooth.SERIAL_PORT_CLASS ],
			    profiles=[ bluetooth.SERIAL_PORT_PROFILE ]			    
			    )
clientSocket, address = serverSocket.accept()

clientSocket.send(LiveViewMessages.EncodeGetCaps())

while True:
	for msg in LiveViewMessages.Decode(clientSocket.recv(4096)):
		# Handle result messages
		if isinstance(msg, LiveViewMessages.Result):
			if msg.code != LiveViewMessages.RESULT_OK:
				print "---------------------------- NON-OK RESULT RECEIVED ----------------------------------"
				print msg
			continue

		# Handling for all other messages
		clientSocket.send(LiveViewMessages.EncodeAck(msg.messageId))
		if isinstance(msg, LiveViewMessages.GetMenuItems):
			clientSocket.send(LiveViewMessages.EncodeGetMenuItemResponse(0, True, 0, "Moo", testPng))
			clientSocket.send(LiveViewMessages.EncodeGetMenuItemResponse(1, False, 20, "Hi1", testPng))
			clientSocket.send(LiveViewMessages.EncodeGetMenuItemResponse(2, False, 0, "Hi2", testPng))
			clientSocket.send(LiveViewMessages.EncodeGetMenuItemResponse(3, True, 0, "Hi3", testPng))

		elif isinstance(msg, LiveViewMessages.GetMenuItem):
			print "---------------------------- GETMENUITEM RECEIVED ----------------------------------"
			# FIXME: do something!

		elif isinstance(msg, LiveViewMessages.DisplayCapabilities):
			deviceCapabilities = msg
			
			clientSocket.send(LiveViewMessages.EncodeSetMenuSize(4))
			clientSocket.send(LiveViewMessages.EncodeSetMenuSettings(menuVibrationTime, 0))

		elif isinstance(msg, LiveViewMessages.GetTime):
			clientSocket.send(LiveViewMessages.EncodeGetTimeResponse(time.time(), is24HourClock))

		elif isinstance(msg, LiveViewMessages.DeviceStatus):
			clientSocket.send(LiveViewMessages.EncodeDeviceStatusAck())

		elif isinstance(msg, LiveViewMessages.GetAlert):
			
			clientSocket.send(LiveViewMessages.EncodeGetAlertResponse(20, 4, 15, "TIME", "HEADER", "01234567890123456789012345678901234567890123456789", testPng))

		elif isinstance(msg, LiveViewMessages.Navigation):
			clientSocket.send(LiveViewMessages.EncodeNavigationResponse(LiveViewMessages.RESULT_EXIT))

	#		clientSocket.send(LiveViewMessages.EncodeSetMenuSize(0))
	#		clientSocket.send(LiveViewMessages.EncodeClearDisplay())
	#		clientSocket.send(LiveViewMessages.EncodeDisplayBitmap(100, 100, testPng))
	#		clientSocket.send(LiveViewMessages.EncodeSetScreenMode(50, False))
	#		clientSocket.send(LiveViewMessages.EncodeDisplayText("WOOOOOOOOOOOO"))

	#		clientSocket.send(LiveViewMessages.EncodeLVMessage(31, ""))


	#		clientSocket.send(LiveViewMessages.EncodeSetScreenMode(0, False))
	#		clientSocket.send(LiveViewMessages.EncodeClearDisplay())
	#		clientSocket.send(LiveViewMessages.EncodeLVMessage(48, struct.pack(">B", 38) + "moo"))

	#		tmpxxx = "MOOO"
	#		clientSocket.send(LiveViewMessages.EncodeSetMenuSize(4))
	#		clientSocket.send(LiveViewMessages.EncodeDisplayText("moo"))

	#		clientSocket.send(LiveViewMessages.EncodeSetStatusBar(tmp.menuItemId, 200, testPng))
			
	#		clientSocket.send(EncodeLVMessage(5, LiveViewMessages.EncodeUIPayload(isAlertItem, totalAlerts, unreadAlerts, curAlert, menuItemId, top, mid, body, itemBitmap)))

			if msg.navType == LiveViewMessages.NAVTYPE_DOWN:
				
				if not msg.wasInAlert:
					clientSocket.send(LiveViewMessages.EncodeDisplayPanel("TOOOOOOOOOOOOOOOOOP", "BOTTTTTTTTTTTTTTTTTOM", testPng, False))
	#			clientSocket.send(LiveViewMessages.EncodeNavigationAck(LiveViewMessages.RESULT_OK))
	#			clientSocket.send(LiveViewMessages.EncodeDisplayText("ADQ WOS HERE"))
	#		elif tmp.navType == LiveViewMessages.NAVTYPE_SELECT:
	#			clientSocket.send(LiveViewMessages.EncodeNavigationAck(LiveViewMessages.RESULT_EXIT))
			
	#		clientSocket.send(LiveViewMessages.EncodeSetVibrate(1, 1000))

		print msg

clientSocket.close()
serverSocket.close()
