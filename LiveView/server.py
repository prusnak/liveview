# this file is licensed under MIT License
# see LICENSE for license details

import messages
import sys
import time
import struct

class Server:

    menuVibrationTime = 5
    is24HourClock = True
    __server = None
    __client = None
    menuItems = []

    def __init__(self):
        self.testPng = open("test.png").read()

    def start(self):
        try:
            import bluetooth
        except:
            print >>sys.stderr, "Python module pybluez not installed."
            sys.exit(1)
        try:
            self.__server = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            self.__server.bind(("",1))
            self.__server.listen(1)
            bluetooth.advertise_service(self.__server, "LiveView", service_classes = [ bluetooth.SERIAL_PORT_CLASS ], profiles = [ bluetooth.SERIAL_PORT_PROFILE ] )
        except:
            print >>sys.stderr, "Could not start a bluetooth server."
            sys.exit(2)
        self.__client, address = self.__server.accept()
        self.__client.send(messages.encodeGetCaps())
        self.__loop()

    def __del__(self):
        if self.__server:
            self.__server.close()
        if self.__client:
            self.__client.close()

    def __send(self, msg):
        self.__client.send(msg)

    def __loop(self):
        while True:
            for msg in messages.decode(self.__client.recv(4096)):
                if isinstance(msg, messages.Result):
                    if msg.code != messages.RESULT_OK:
                        print "---- NON-OK result received ----"
                        print msg
                        continue

                self.__send(messages.encodeAck(msg.messageId))

                if isinstance(msg, messages.GetMenuItems):
                    for idx, item in enumerate(self.items):
                        self.__send(messages.encodeGetMenuItemResponse(idx, item.isAlert, item.unreadCount, item.text, item.bitmap))

                elif isinstance(msg, messages.GetMenuItem):
                    print "---- GetMenuItem received ----"
                    # FIXME: do something!

                elif isinstance(msg, messages.DisplayCapabilities):
                    deviceCapabilities = msg
                    self.__send(messages.encodeSetMenuSize(len(self.menuItems)))
                    self.__send(messages.encodeSetMenuSettings(self.menuVibrationTime, 0))

                elif isinstance(msg, messages.GetTime):
                    self.__send(messages.encodeGetTimeResponse(time.time(), self.is24HourClock))

                elif isinstance(msg, messages.DeviceStatus):
                    self.__send(messages.encodeDeviceStatusAck())

                elif isinstance(msg, messages.GetAlert):
                    pass
                    # FIXME: fill implementation

                elif isinstance(msg, messages.Navigation):
                    self.__send(messages.encodeNavigationResponse(messages.RESULT_EXIT))
                    # FIXME: handle events according to navType

                print msg

    def setMenuItems(self, items):
        self.menuItems = items
