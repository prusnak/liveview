import struct
import time
import sys

CLIENT_SOFTWARE_VERSION = "0.0.3"

MSG_GETCAPS             = 1
MSG_GETCAPS_RESP        = 2

MSG_DISPLAYTEXT         = 3
MSG_DISPLAYTEXT_ACK     = 4

MSG_DISPLAYPANEL        = 5
MSG_DISPLAYPANEL_ACK    = 6

MSG_DEVICESTATUS        = 7
MSG_DEVICESTATUS_ACK    = 8

MSG_DISPLAYBITMAP       = 19
MSG_DISPLAYBITMAP_ACK   = 20

MSG_CLEARDISPLAY        = 21
MSG_CLEARDISPLAY_ACK    = 22

MSG_SETMENUSIZE         = 23
MSG_SETMENUSIZE_ACK     = 24

MSG_GETMENUITEM         = 25
MSG_GETMENUITEM_RESP    = 26

MSG_GETALERT            = 27
MSG_GETALERT_RESP       = 28

MSG_NAVIGATION          = 29
MSG_NAVIGATION_RESP     = 30

MSG_SETSTATUSBAR        = 33
MSG_SETSTATUSBAR_ACK    = 34

MSG_GETMENUITEMS        = 35

MSG_SETMENUSETTINGS     = 36
MSG_SETMENUSETTINGS_ACK = 37

MSG_GETTIME             = 38
MSG_GETTIME_RESP        = 39

MSG_SETLED              = 40
MSG_SETLED_ACK          = 41

MSG_SETVIBRATE          = 42
MSG_SETVIBRATE_ACK      = 43

MSG_ACK                 = 44

MSG_SETSCREENMODE       = 64
MSG_SETSCREENMODE_ACK   = 65

MSG_GETSCREENMODE       = 66
MSG_GETSCREENMODE_RESP  = 67

DEVICESTATUS_OFF        = 0
DEVICESTATUS_ON         = 1
DEVICESTATUS_MENU       = 2

RESULT_OK               = 0
RESULT_ERROR            = 1
RESULT_OOM              = 2
RESULT_EXIT             = 3
RESULT_CANCEL           = 4

NAVACTION_PRESS         = 0
NAVACTION_LONGPRESS     = 1
NAVACTION_DOUBLEPRESS   = 2

NAVTYPE_UP              = 0
NAVTYPE_DOWN            = 1
NAVTYPE_LEFT            = 2
NAVTYPE_RIGHT           = 3
NAVTYPE_SELECT          = 4
NAVTYPE_MENUSELECT      = 5

ALERTACTION_CURRENT     = 0
ALERTACTION_FIRST       = 1
ALERTACTION_LAST        = 2
ALERTACTION_NEXT        = 3
ALERTACTION_PREV        = 4

BRIGHTNESS_OFF          = 48
BRIGHTNESS_DIM          = 49
BRIGHTNESS_MAX          = 50


def DecodeLVMessage(msg):
    (messageId, headerLen, payloadLen) = struct.unpack(">BBL", msg[0:6])
    msgLength = 2 + headerLen + payloadLen
    payload = msg[2 + headerLen: msgLength]

    if headerLen != 4:
        raise Exception("Unexpected header length %i" % headerLen)
    if payloadLen != len(payload):
        i = 0
        for x in msg:
            print >>sys.stderr, "\t%02x: %02x" % (i, ord(x))
            i += 1
        raise Exception("Payload length is not as expected %i != %i", (payloadLen, len(payload)))

    return (messageId, payload, msgLength)

def Decode(msg):
    result = []
    consumed = 0
    while consumed < len(msg):
        (messageId, payload, msgLength) = DecodeLVMessage(msg[consumed:])
        consumed += msgLength

        if messageId == MSG_GETCAPS_RESP:
            result.append(DisplayCapabilities(messageId, payload))
        elif messageId == MSG_SETLED_ACK:
            result.append(Result(messageId, payload))
        elif messageId == MSG_SETVIBRATE_ACK:
            result.append(Result(messageId, payload))
        elif messageId == MSG_DEVICESTATUS_ACK:
            result.append(Result(messageId, payload))
        elif messageId == MSG_SETSCREENMODE_ACK:
            result.append(Result(messageId, payload))
        elif messageId == MSG_CLEARDISPLAY_ACK:
            result.append(Result(messageId, payload))
        elif messageId == MSG_SETSTATUSBAR_ACK:
            result.append(Result(messageId, payload))
        elif messageId == MSG_DISPLAYTEXT_ACK:
            result.append(Result(messageId, payload))
        elif messageId == MSG_DISPLAYBITMAP_ACK:
            result.append(Result(messageId, payload))
        elif messageId == MSG_DISPLAYPANEL_ACK:
            result.append(Result(messageId, payload))
        elif messageId == MSG_GETMENUITEMS:
            result.append(GetMenuItems(messageId, payload))
        elif messageId == MSG_GETMENUITEM:
            result.append(GetMenuItem(messageId, payload))
        elif messageId == MSG_GETTIME:
            result.append(GetTime(messageId, payload))
        elif messageId == MSG_GETALERT:
            result.append(GetAlert(messageId, payload))
        elif messageId == MSG_DEVICESTATUS:
            result.append(DeviceStatus(messageId, payload))
        elif messageId == MSG_NAVIGATION:
            result.append(Navigation(messageId, payload))
        elif messageId == MSG_GETSCREENMODE_RESP:
            result.append(GetScreenMode(messageId, payload))
        else:
            print >>sys.stderr, "Unknown message id %i" % messageId
            i = 0
            for x in payload:
                print >>sys.stderr, "\t%02x: %02x" % (i, ord(x))
                i += 1

    return result

def EncodeLVMessage(messageId, data):
    return struct.pack(">BBL", messageId, 4, len(data)) + data

def EncodeGetCaps():
    return EncodeLVMessage(MSG_GETCAPS, struct.pack(">B", len(CLIENT_SOFTWARE_VERSION)) + CLIENT_SOFTWARE_VERSION)

def EncodeSetVibrate(delayTime, onTime):
    return EncodeLVMessage(MSG_SETVIBRATE, struct.pack(">HH", delayTime, onTime))

def EncodeSetLED(r, g, b, delayTime, onTime):
    return EncodeLVMessage(MSG_SETLED, struct.pack(">HHH", ((r & 0x31) << 10) | ((g & 0x31) << 5) | (b & 0x31), delayTime, onTime))

def EncodeSetMenuSize(menuSize):
    return EncodeLVMessage(MSG_SETMENUSIZE, struct.pack(">B", menuSize))

def EncodeAck(ackMessageId):
    return EncodeLVMessage(MSG_ACK, struct.pack(">B", ackMessageId))

def EncodeDeviceStatusAck():
    return EncodeLVMessage(MSG_DEVICESTATUS_ACK, struct.pack(">B", RESULT_OK))

def EncodeGetMenuItemResponse(menuItemId, isAlertItem, unreadCount, text, itemBitmap):
    payload = struct.pack(">BHHHBB", not isAlertItem, 0, unreadCount, 0, menuItemId + 3, 0)    # final 0 is for plaintext vs bitmapimage (1) strings
    payload += struct.pack(">H", 0)             # unused string
    payload += struct.pack(">H", 0)             # unused string
    payload += struct.pack(">H", len(text)) + text
    payload += itemBitmap

    return EncodeLVMessage(MSG_GETMENUITEM_RESP, payload)

def EncodeDisplayPanel(topText, bottomText, bitmap, alertUser):

    id = 80
    if not alertUser:
        id |= 1

    payload = struct.pack(">BHHHBB", 0, 0, 0, 0, id, 0)    # final 0 is for plaintext vs bitmapimage (1) strings
    payload += struct.pack(">H", len(topText)) + topText
    payload += struct.pack(">H", 0)             # unused string
    payload += struct.pack(">H", len(bottomText)) + bottomText
    payload += bitmap

    return EncodeLVMessage(MSG_DISPLAYPANEL, payload)

def EncodeDisplayBitmap(x, y, bitmap):
    # Only works if you have sent SetMenuItems(0)
    # Meaning of byte 2 is unknown, but /is/ important!
    return EncodeLVMessage(MSG_DISPLAYBITMAP, struct.pack(">BBB", x, y, 1) + bitmap)

def EncodeSetStatusBar(menuItemId, unreadAlerts, itemBitmap):
    # Note that menu item#0 is treated specially if you have non-zero unreadAlerts...
    # Its value will be automatically updated from the other menu items... e.g. if item #3 currently has 20, and is changed to 200 with this call, item#0 will automatically be set to 180 (200-20). Slightly annoying!

    payload = struct.pack(">BHHHBB", 0, 0, unreadAlerts, 0, menuItemId + 3, 0)
    payload += struct.pack(">H", 0)
    payload += struct.pack(">H", 0)
    payload += struct.pack(">H", 0)
    payload += itemBitmap

    return EncodeLVMessage(MSG_SETSTATUSBAR, payload)

def EncodeGetTimeResponse(time, is24HourDisplay):
    return EncodeLVMessage(MSG_GETTIME_RESP, struct.pack(">LB", time, not is24HourDisplay))

def EncodeNavigationResponse(result):
    return EncodeLVMessage(MSG_NAVIGATION_RESP, struct.pack(">B", result))

def EncodeSetScreenMode(brightness, auto):
    # Only works if you have sent SetMenuItems(0)
    v = brightness << 1
    if auto:
        v |= 1
    return EncodeLVMessage(MSG_SETSCREENMODE, struct.pack(">B", v))

def EncodeGetScreenMode():
    # Only works if you have sent SetMenuItems(0)
    return EncodeLVMessage(MSG_GETSCREENMODE, "")

def EncodeClearDisplay():
    # Only works if you have sent SetMenuItems(0)
    return EncodeLVMessage(MSG_CLEARDISPLAY, "")

def EncodeSetMenuSettings(vibrationTime, initialMenuItemId):
    # This message is never acked for some reason.
    # vibrationTime is in units of approximately 100ms

    return EncodeLVMessage(MSG_SETMENUSETTINGS, struct.pack(">BBB", vibrationTime, 12, initialMenuItemId)) # 12 is "font size" - doesn't seem to change anything though!

def EncodeGetAlertResponse(totalCount, unreadCount, alertIndex, timestampText, headerText, bodyTextChunk, bitmap):
    payload = struct.pack(">BHHHBB", 0, totalCount, unreadCount, alertIndex, 0, 0)    # final 0 is for plaintext vs bitmapimage (1) strings
    payload += struct.pack(">H", len(timestampText)) + timestampText
    payload += struct.pack(">H", len(headerText)) + headerText
    payload += struct.pack(">H", len(bodyTextChunk)) + bodyTextChunk
    payload += struct.pack(">B", 0)
    payload += struct.pack(">L", len(bitmap)) + bitmap

    return EncodeLVMessage(MSG_GETALERT_RESP, payload)

def EncodeDisplayText(s):
    # FIXME: doesn't seem to do anything!
    return EncodeLVMessage(MSG_DISPLAYTEXT, struct.pack(">B", 0) + s)


class DisplayCapabilities:

    def __init__(self, messageId, msg):
        self.messageId = messageId
        (self.width, self.height, self.statusBarWidth, self.statusBarHeight, self.viewWidth, self.viewHeight, self.announceWidth, self.announceHeight, self.textChunkSize, idleTimer) = struct.unpack(">BBBBBBBBBB", msg[0:10])
        self.softwareVersion = msg[10:]

        if idleTimer != 0:
            print >>sys.stderr, "DisplayCapabilities with non-zero idle timer %i" % idleTimer

    def __str__(self):
        return "<DisplayCapabilities Width:%i Height:%i StatusBarWidth:%i StatusBarHeight:%i ViewWidth:%i ViewHeight:%i AnnounceWidth:%i AnnounceHeight:%i TextChunkSize:%i SoftwareVersion:%s>" % (self.width, self.height, self.statusBarWidth, self.statusBarHeight, self.viewWidth, self.viewHeight, self.announceWidth, self.announceHeight, self.textChunkSize, self.softwareVersion)

class Result:

    def __init__(self, messageId, msg):
        self.messageId = messageId
        (self.code, ) = struct.unpack(">B", msg)
        if self.code > RESULT_CANCEL:
            print >>sys.stderr, "Result with unknown code %i" % self.code

    def __str__(self):
        s = "UNKNOWN"
        if self.code == RESULT_OK:
            s = "OK"
        elif self.code == RESULT_ERROR:
            s = "ERROR"
        elif self.code == RESULT_OOM:
            s = "OOM"
        elif self.code == RESULT_EXIT:
            s = "EXIT"
        elif self.code == RESULT_CANCEL:
            s = "CANCEL"

        return "<Result MessageId:%i Code:%s>" % (self.messageId, s)

class GetMenuItem:

    def __init__(self, messageId, msg):
        self.messageId = messageId
        (self.menuItemId, ) = struct.unpack(">B", msg)

    def __str__(self):
        return "<GetMenuItem MenuItemId:%i>" % self.menuItemId

class GetMenuItems:

    def __init__(self, messageId, msg):
        self.messageId = messageId
        (unknown, ) = struct.unpack(">B", msg)
        if unknown != 0:
            print >>sys.stderr, "GetMenuItems with non-zero unknown byte %i" % unknown

    def __str__(self):
        return "<GetMenuItems>"

class GetTime:

    def __init__(self, messageId, msg):
        self.messageId = messageId
        (unknown, ) = struct.unpack(">B", msg)
        if unknown != 0:
            print >>sys.stderr, "GetTime with non-zero unknown byte %i" % unknown

    def __str__(self):
        return "<GetTime>"

class DeviceStatus:

    def __init__(self, messageId, msg):
        self.messageId = messageId
        (self.deviceStatus, ) = struct.unpack(">B", msg)
        if self.deviceStatus > 2:
            print >>sys.stderr, "DeviceStatus with unknown value %i" % self.deviceStatus

    def __str__(self):
        s = "UNKNOWN"
        if self.deviceStatus == DEVICESTATUS_OFF:
            s = "Off"
        elif self.deviceStatus == DEVICESTATUS_ON:
            s = "On"
        elif self.deviceStatus == DEVICESTATUS_MENU:
            s = "Menu"

        return "<DeviceStatus Status:%s>" % s

class GetAlert:

    def __init__(self, messageId, msg):
        self.messageId = messageId

        (self.menuItemId, self.alertAction, self.maxBodySize, a, b, c) = struct.unpack(">BBHBBB", msg)
        if a != 0 or b != 0  or c != 0:
            print >>sys.stderr, "GetAlert with non zero text values! %i %i %i" % (a, b, c)
        if self.alertAction > ALERTACTION_PREV:
            print >>sys.stderr, "GetAlert with out of range action %i" % self.alertAction

    def __str__(self):
        s = "UNKNOWN"
        if self.alertAction == ALERTACTION_CURRENT:
            s = "Current"
        elif self.alertAction == ALERTACTION_FIRST:
            s = "First"
        elif self.alertAction == ALERTACTION_LAST:
            s = "Last"
        elif self.alertAction == ALERTACTION_NEXT:
            s = "Next"
        elif self.alertAction == ALERTACTION_PREV:
            s = "Previous"

        return "<GetAlert MenuItemId:%i AlertAction:%s MaxBodyLength:%i>" % (self.menuItemId, s, self.maxBodySize)

class Navigation:

    def __init__(self, messageId, msg):
        self.messageId = messageId
        (byte0, byte1, navigation, self.menuItemId, menuId) = struct.unpack(">BBBBB", msg)
        if byte0 != 0:
            print >>sys.stderr, "Navigation with unknown byte0 value %i" % byte0
        if byte1 != 3:
            print >>sys.stderr, "Navigation with unknown byte1 value %i" % byte1
        if menuId != 10 and menuId != 20:
            print >>sys.stderr, "Navigation with unexpected menuId value %i" % menuId
        if (navigation != 32) and ((navigation < 1) or (navigation > 15)):
            print >>sys.stderr, "Navigation with out of range value %i" % navigation

        self.wasInAlert = menuId == 20

        if navigation != 32:
            self.navAction = (navigation - 1) % 3
            self.navType = int((navigation - 1) / 3)
        else:
            self.navAction = NAVACTION_PRESS
            self.navType = NAVTYPE_MENUSELECT

    def __str__(self):

        sA = "UNKNOWN"
        if self.navAction == NAVACTION_PRESS:
            sA = "Press"
        elif self.navAction == NAVACTION_DOUBLEPRESS:
            sA = "DoublePress"
        elif self.navAction == NAVACTION_LONGPRESS:
            sA = "LongPress"

        sT = "UNKNOWN"
        if self.navType == NAVTYPE_UP:
            sT = "Up"
        elif self.navType == NAVTYPE_DOWN:
            sT = "Down"
        elif self.navType == NAVTYPE_LEFT:
            sT = "Left"
        elif self.navType == NAVTYPE_RIGHT:
            sT = "Right"
        elif self.navType == NAVTYPE_SELECT:
            sT = "Select"
        elif self.navType == NAVTYPE_MENUSELECT:
            sT = "MenuSelect"

        return "<Navigation Action:%s Type:%s MenuItemId:%i WasInAlert:%i>" % (sA, sT, self.menuItemId, self.wasInAlert)

class GetScreenMode:

    def __init__(self, messageId, msg):
        self.messageId = messageId
        (raw, ) = struct.unpack(">B", msg)
        self.auto = raw & 1
        self.brightness = raw >> 1

    def __str__(self):
        return "<GetScreenMode Auto:%i Brightness:%i>" % (self.auto, self.brightness)
