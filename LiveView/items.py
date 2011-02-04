# this file is licensed under the Modified BSD License
# see LICENSE for license details

class MenuItem:

    def __init__(self, isAlert, unreadCount, text, bitmap):
        self.isAlert = isAlert
        self.unreadCount = unreadCount
        self.text = text
        self.bitmap = bitmap

class AlertResponse:

    def __init__(totalCount, unreadCount, alertIndex, timestampText, headerText, bodyText, bitmap):
        self.totalCount = totalCount
        self.unreadCount = unreadCount
        self.alertIndex = alertIndex
        self.timestampText = timestampText
        self.headerText = headerText
        self.bodyText = bodyText
        self.bitmap = bitmap

class DisplayPanel:

    def __init__(topText, bottomText, bitmap, alertUser):
        self.topText = topText
        self.bottomText = bottomText
        self.bitmap = bitmap
        self.alertUser = alertUser
