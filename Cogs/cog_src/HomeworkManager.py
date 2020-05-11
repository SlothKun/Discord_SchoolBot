from .Homework import Homework, HomeworkMessage

from string import Template
from datetime import datetime

class HomeworkManager():

    HMW_ACTIONS = ["hmwAdd", "hmwEdit", "hmwDelete"]
    HMW_EMOJIS = ["back", "cancel", "addFile", "modifConf"]
    MAX_HMW_AGE = 600 #Maximum age for an homework (in seconds)

    def __init__(self, dbStructJson, mDB):
        self._homeworks = {}
        self._linkedChannel = {}
        self._linkedBotMsg = {}
        self._hmwRecap = {}

        # Homework collection elements
        self.hmwCol = mDB[dbStructJson['db_collections']['homework']]
        self.hmwFields = {
            'date': dbStructJson['db_collections']['homework_fields']['deadline'],
            'subject': dbStructJson['db_collections']['homework_fields']['subject'],
            'name': dbStructJson['db_collections']['homework_fields']['name']
        }

        # Emoji collection elements
        hmwEmojiCol = mDB[dbStructJson['db_collections']['emoji']]

        idField = dbStructJson['db_collections']['emoji_fields']['id']
        nameField = dbStructJson['db_collections']['emoji_fields']['name']
        valueField = dbStructJson['db_collections']['emoji_fields']['value']

        self.emojiList = {
            HomeworkManager.HMW_EMOJIS[0] : hmwEmojiCol.find({nameField: 'back'}, {idField: 0, valueField: 1})[0][valueField],
            HomeworkManager.HMW_EMOJIS[1] : hmwEmojiCol.find({nameField: 'cross'}, {idField: 0, valueField: 1})[0][valueField],
            HomeworkManager.HMW_EMOJIS[2] : hmwEmojiCol.find({nameField: 'check'}, {idField: 0, valueField: 1})[0][valueField],
            HomeworkManager.HMW_EMOJIS[3] : hmwEmojiCol.find({nameField: 'confModif'}, {idField: 0, valueField: 1})[0][valueField],
            HomeworkManager.HMW_ACTIONS[0] : hmwEmojiCol.find({nameField: 'add'}, {idField: 0, valueField: 1})[0][valueField],
            HomeworkManager.HMW_ACTIONS[1] : hmwEmojiCol.find({nameField: 'edit'}, {idField: 0, valueField: 1})[0][valueField],
            HomeworkManager.HMW_ACTIONS[2] : hmwEmojiCol.find({nameField: 'delete'}, {idField: 0, valueField: 1})[0][valueField]
        }
    
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

    def groupHmwByDate(self, hmwList):
        res = {}
        for hmw in hmwList:
            hmwDate = hmw[self.hmwFields['date']].strftime('%d %B %Y')
            if hmwDate in res:
                res[hmwDate].append(hmw)
            else:
                res[hmwDate] = [hmw]
        return res

    def listHmw(self):
        # Get all homework with a deadline greater than the current time
        print(datetime.utcnow())
        print(self.hmwCol.count_documents({}))
        print(self.hmwCol.count_documents({self.hmwFields['date']: {'lte': datetime.now()}}))
        print(self.hmwCol.count_documents({self.hmwFields['date']: {'gte': datetime.utcnow()}}))
        homeworks = self.hmwCol.find({})
        for hmw in homeworks:
            print(hmw[self.hmwFields['date']])
            print(hmw[self.hmwFields['date']] >= datetime.utcnow())
            print(hmw[self.hmwFields['date']] >= datetime.now())
        homeworks = self.hmwCol.find({self.hmwFields['date']: {'gte': datetime.utcnow()}})
        emojis = [self.emojiList[HomeworkManager.HMW_ACTIONS[0]], self.emojiList[HomeworkManager.HMW_ACTIONS[1]], self.emojiList[HomeworkManager.HMW_ACTIONS[2]]]

        # Formatting the listing homework message before sending it
        formatedHmwList = HomeworkMessage.HMW_UTILS['formatingQuote']
        groupedHmw = self.groupHmwByDate(homeworks)
        print(groupedHmw)
        for hmwDate in groupedHmw:
            formatedHmwList += f"\n{hmwDate}"
            for homework in groupedHmw[hmwDate]:
                formatedHmwList += f"\n\t- {homework[self.hmwFields['subject']]} : {homework[self.hmwFields['name']]}"
            formatedHmwList += "\n"
        formatedHmwList += HomeworkMessage.HMW_UTILS['separationLine']
        formatedHmwList += f"\n\t{emojis[0]} - Ajouter un devoir"
        formatedHmwList += f"\n\t{emojis[1]} - Éditer un devoir"
        formatedHmwList += f"\n\t{emojis[2]} - Supprimer un devoir"
        formatedHmwList += HomeworkMessage.HMW_UTILS['formatingQuote']

        return (formatedHmwList, emojis)

    def newHmw(self, creatorID, hmwAction, channelID, botMsgID):
        print(f"HOMEWORK_MAN - Creating a new homework for {creatorID} in mode {HomeworkManager.HMW_ACTIONS[hmwAction]}")
        self.homeworks[creatorID] = Homework(creatorID, HomeworkManager.HMW_ACTIONS[hmwAction], self.hmwObserver)
        self.linkedChannel[creatorID] = channelID
        self.linkedBotMsg[creatorID] = botMsgID

        res = HomeworkMessage.HMW_ADD['title'].substitute(stepNum = self.homeworks[creatorID].stateIdx + 1, totalStep = self.homeworks[creatorID].nbStep)
        res += HomeworkMessage.HMW_UTILS['formatingQuote']
        res += HomeworkMessage.HMW_ADD[self.homeworks[creatorID].state].substitute()
        res += HomeworkMessage.HMW_UTILS['separationLine']
        res += HomeworkMessage.HMW_UTILS['cancel'].substitute(emoji = self.emojiList[HomeworkManager.HMW_EMOJIS[1]], userAction = self.homeworks[creatorID].userActionName)
        res += HomeworkMessage.HMW_UTILS['formatingQuote']
        return res

    def deleteHmw(self, creatorID, channelID):
        if self.checkHmw(creatorID, channelID):
            del self.homeworks[creatorID]
            del self.linkedChannel[creatorID]
            del self.linkedBotMsg[creatorID]
            return True
        return False

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
        currentHmw = self.homeworks[creatorID]
        if not isBack:
            if not currentHmw.isComplete:
                # Send the new value to the corresponding homework
                # updateStatus = self.homeworks[creatorID].updateVal(value, isBack)
                (updateRes, msgBack) = currentHmw.updateVal(value, isBack)

                emojis = []
                emojiIDs = [HomeworkManager.HMW_EMOJIS[0], HomeworkManager.HMW_EMOJIS[1]]

                if not currentHmw.docAwaited:
                    emojiIDs.append(HomeworkManager.HMW_EMOJIS[2])
                if currentHmw.isComplete:
                    emojiIDs.append(HomeworkManager.HMW_EMOJIS[3])

                res = currentHmw.lastChange
                res += "\n\n" + HomeworkMessage.HMW_ADD['title'].substitute(stepNum = currentHmw.stateIdx + 1, totalStep = currentHmw.nbStep)
                res += HomeworkMessage.HMW_UTILS['formatingQuote']
                res += msgBack
                res += HomeworkMessage.HMW_UTILS['separationLine']
                for emojiID in emojiIDs:
                    res += HomeworkMessage.HMW_UTILS[emojiID].substitute(emoji = self.emojiList[emojiID], userAction = currentHmw.userActionName)
                    emojis.append(self.emojiList[emojiID])
                res += HomeworkMessage.HMW_UTILS['formatingQuote']
                return (res, emojis)
            return (None, None)
        else:
            if currentHmw.isComplete:
                currentHmw.isComplete = False
            
            (updateRes, msgBack) = currentHmw.updateVal(value, isBack)

            emojis = []
            emojiIDs = [HomeworkManager.HMW_EMOJIS[0], HomeworkManager.HMW_EMOJIS[1]]

            if not currentHmw.docAwaited:
                emojiIDs.append(HomeworkManager.HMW_EMOJIS[2])
            if currentHmw.isComplete:
                emojiIDs.append(HomeworkManager.HMW_EMOJIS[3])

            res = currentHmw.lastChange
            res += "\n\n" + HomeworkMessage.HMW_ADD['title'].substitute(stepNum = currentHmw.stateIdx + 1, totalStep = currentHmw.nbStep)
            res += HomeworkMessage.HMW_UTILS['formatingQuote']
            res += msgBack
            res += HomeworkMessage.HMW_UTILS['separationLine']
            for emojiID in emojiIDs:
                res += HomeworkMessage.HMW_UTILS[emojiID].substitute(emoji = self.emojiList[emojiID], userAction = currentHmw.userActionName)
                emojis.append(self.emojiList[emojiID])
            res += HomeworkMessage.HMW_UTILS['formatingQuote']
            return (res, emojis)
        
    def checkHmwFileStatus(self, creatorID):
        return self.homeworks[creatorID].docAwaited

    def setHmwDoc(self, creatorID, newFile):
        self.homeworks[creatorID].doc = newFile

    def setDoc(self, creatorID):
        currentHmw = self.homeworks[creatorID]
        msgBack = currentHmw.updateDocStatus(True)

        emojis = []
        emojiIDs = [HomeworkManager.HMW_EMOJIS[0], HomeworkManager.HMW_EMOJIS[1]]

        if currentHmw.isComplete:
            emojiIDs.append(HomeworkManager.HMW_EMOJIS[3])

        res = HomeworkMessage.HMW_CONF['docUpdated'].substitute()
        res += "\n\n" + HomeworkMessage.HMW_ADD['title'].substitute(stepNum = currentHmw.stateIdx + 1, totalStep = currentHmw.nbStep)
        res += HomeworkMessage.HMW_UTILS['formatingQuote']
        res += msgBack
        res += HomeworkMessage.HMW_UTILS['separationLine']
        for emojiID in emojiIDs:
            res += HomeworkMessage.HMW_UTILS[emojiID].substitute(emoji = self.emojiList[emojiID], userAction = currentHmw.userActionName)
            emojis.append(self.emojiList[emojiID])
        res += HomeworkMessage.HMW_UTILS['formatingQuote']
        return (res, emojis)
    
    def getHmwDict(self, creatorID):
        hmwDict = self.homeworks[creatorID].hmwDict()

        res = HomeworkMessage.HMW_CONF['dbUpdated'].substitute()
        (listHmw, emojis) = self.listHmw()
        res += listHmw

        return (hmwDict, res, emojis)