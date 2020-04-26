from .Homework import Homework

from string import Template

class HomeworkMessage():
    HMW_UTILS = {
        "formatingQuote": "```",
        "separationLine" : "\n\n-----------------\nCliquez sur les réactions en-dessous du message pour interagir des façons suivantes:",

        "cancelOption": Template("\n\t$cancelEmoji - Annuler $userAction du devoir"),
        "backOption": Template("\n\t$backEmoji - Annuler dernière action"),
        "addFileOption": Template("\n\t$addFileEmoji - Ajouter un document au devoir"),
        "hmwModifConf": Template("\n\t$confEmoji - Confirmer $userAction du devoir")
    }

    HMW_ADD = {
        "title": Template("**Ajout d'un nouveau devoir - Étape $stepNum/$totalStep**\n"),

        "idle": "Veuillez préciser le nom du devoir que vous souhaitez créer \n\t - ex: 'Devoir maison #1'",
        "name": Template("Veuillez préciser la date limite du devoir que vous souhaitez créer \n\tLe format de la date doit être le suivant '$dateFormat' - ex: $dateExample"),
        "date": "Veuillez préciser le statut du devoir que vous souhaitez créer \n\t - ex: 'À rendre', 'Obligatoire'",
        "status": "Veuillez préciser la matière du devoir que vous souhaitez créer \n\t - ex: 'Mathématiques', 'Physique'",
        "subject": Template("$hmwRecap")
    }

    HMW_EDIT = {}

    HMW_DELETE = {}

    HMW_CONF = {
        "name": Template("Nom $var a bien été enregistré"),
        "date": Template("Date $var a bien été enregistrée"),
        "status": Template("Status $var a bien été enregistré"),
        "subject": Template("Matière $var a bien été enregistrée"),

        "backMessage": "Dernière modification ($lastModif) a bien été annulée",
        "cancelMessage": Template("$userAction du devoir a bien été annulé")
    }

    @classmethod
    def addHmwBoxBuilder(cls, hmwState, emojis):
        res = [HomeworkMessage.HMW_UTILS['formatingQuote']]
        res.append(HomeworkMessage.HMW_ADD[hmwState])
        res.append(HomeworkMessage.HMW_UTILS['separationLine'])
        for emoji in emojis:
            if emoji == "cancel":
                res.append(HomeworkMessage.HMW_UTILS['cancelOption'])
            elif emoji == "back":
                res.append(HomeworkMessage.HMW_UTILS['backOption'])
            elif emoji == "addFile":
                res.append(HomeworkMessage.HMW_UTILS['addFileOption'])
            elif emoji == "modifConf":
                res.append(HomeworkMessage.HMW_UTILS['hmwModifConf'])
        res.append(HomeworkMessage.HMW_UTILS['formatingQuote'])
        return res

class HomeworkManager():

    HMW_ACTIONS = ["hmwAdd", "hmwEdit", "hmwDelete"]
    MAX_HMW_AGE = 600 #Maximum age for an homework (in seconds)

    def __init__(self, dbStructJson, mDB):
        self._homeworks = {}
        self._linkedChannel = {}
        self._linkedBotMsg = {}
        self._docBotMsg = {}
        self._hmwRecap = {}

        hmwEmojiDB = mDB[dbStructJson['db_collections']['emoji']]
        self.addFileEmoji = hmwEmojiDB.find({dbStructJson['db_collections']['emoji_fields']['name']: 'check'}, {'value': 1})[0][dbStructJson['db_collections']['emoji_fields']['value']]
        self.cancelEmoji = hmwEmojiDB.find({dbStructJson['db_collections']['emoji_fields']['name']: 'cross'}, {'value': 1})[0][dbStructJson['db_collections']['emoji_fields']['value']]
        self.backEmoji = hmwEmojiDB.find({dbStructJson['db_collections']['emoji_fields']['name']: 'back'}, {'value': 1})[0][dbStructJson['db_collections']['emoji_fields']['value']]
        self.confModifEmoji = hmwEmojiDB.find({dbStructJson['db_collections']['emoji_fields']['name']: 'confModif'}, {'value': 1})[0][dbStructJson['db_collections']['emoji_fields']['value']]
    
    def __str__(self):
        res =  f"HomeworkManager currently keep track of {len(self.homeworks)} homework(s):"
        for hmw in self.homeworks:
            res += f"\n\t{hmw.id} - {hmw.name} in {hmw.userAction} mode"
        return res

    ## GETTERs
    @property
    def homeworks(self):
        return self._homeworks

    @property
    def linkedChannel(self):
        return self._linkedChannel

    @property
    def linkedBotMsg(self):
        return self._linkedBotMsg

    @property
    def docBotMsg(self):
        return self._docBotMsg

    @property
    def hmwRecap(self):
        return self._hmwRecap

    def hmwObserver(self, creatorID, hmwComplete):
        print(f"HOMEWORK_MAN - Observer called by hmw[{creatorID}]")
        hmw = self.homeworks[creatorID]
        res = ""
        if hmw.userAction == HomeworkManager.HMW_ACTIONS[0]:
            ## Adding an homework
            res += f"{hmw}"
            if not hmwComplete:
                # All data are filled but the related document expected
                res += "\nVous avez spécifié qu'un document devait être lié au devoir, mais aucun document n'a été reçu."
                res += "\nVeuillez glisser un document dans ce salon ou ignorez ce message pour valider l'ajout du document"
            res 
        elif hmw.userAction == HomeworkManager.HMW_ACTIONS[1]:
            ## Editing an homework
            pass
        elif hmw.userAction == HomeworkManager.HMW_ACTIONS[2]:
            ## Deleting an homework
            pass
        self.hmwRecap[creatorID] = res

    def checkHmw(self, creatorID, channelID):
        if creatorID in self.homeworks:
            return self.linkedChannel[creatorID] == channelID
        else:
            return False

    def checkHmwValidity(self, creatorID):
        if (self.homeworks[creatorID].age > HomeworkManager.MAX_HMW_AGE):
            del self.homeworks[creatorID]
            return False
        else:
            return True

    def newHmw(self, creatorID, hmwAction, channelID, botMsgID):
        print(f"HOMEWORK_MAN - Creating a new homework for {creatorID} in mode {HomeworkManager.HMW_ACTIONS[hmwAction]}")
        self.homeworks[creatorID] = Homework(creatorID, HomeworkManager.HMW_ACTIONS[hmwAction], self.hmwObserver)
        self.linkedChannel[creatorID] = channelID
        self.linkedBotMsg[creatorID] = botMsgID

        res = HomeworkMessage.HMW_ADD['title'].substitute(stepNum = self.homeworks[creatorID].stateIdx + 1, totalStep = self.homeworks[creatorID].nbStep)
        res += HomeworkMessage.HMW_UTILS['formatingQuote']
        res += HomeworkMessage.HMW_ADD[self.homeworks[creatorID].state]
        res += HomeworkMessage.HMW_UTILS['separationLine']
        res += HomeworkMessage.HMW_UTILS['cancelOption'].substitute(cancelEmoji = self.cancelEmoji, userAction = self.homeworks[creatorID].userActionName)
        res += HomeworkMessage.HMW_UTILS['formatingQuote']
        return res

    def checkHmwState(self, creatorID):
        if self.homeworks[creatorID].state == HomeworkManager.substates[self.homeworks[creatorID].userAction][-1] and self.homeworks[creatorID].isComplete():
            return True
        return False

    # def updateBotMsg(self, creatorID, newBotMsgID):
    #     self.linkedBotMsg[creatorID] = newBotMsgID

    def getNbSubState(self, creatorID):
        return self.homeworks[creatorID].nbStep

    def getHmwState(self, creatorID):
        return self.homeworks[creatorID].state

    def getHmwLastError(self, creatorID):
        return self.homeworks[creatorID].lastError

    def getHmwLastChange(self, creatorID):
        return self.homeworks[creatorID].lastChange

    def updateHmw(self, creatorID, value, isBack = False):
        # Send the new value to the corresponding homework
        # updateStatus = self.homeworks[creatorID].updateVal(value, isBack)
        res = ""
        emojis = []
        if self.homeworks[creatorID].updateVal(value, isBack):
            if self.homeworks[creatorID].state == "date":
                value = value.strftime('%Y-%m-%d')
            res = HomeworkMessage.HMW_CONF[self.homeworks[creatorID].state].substitute(value)
            res += "\n" + HomeworkMessage.HMW_ADD['title'].substitute(stepNum = self.homeworks[creatorID].stateIdx + 1, totalStep = self.homeworks[creatorID].nbStep)
        return False
        
    def checkHmwFileStatus(self, creatorID):
        return self.homeworks[creatorID].docAwaited

    def setHmwDoc(self, creatorID, newFile):
        self.homeworks[creatorID].doc = newFile

    def setDocMsg(self, creatorID, messageID):
        self.docBotMsg[creatorID] = messageID