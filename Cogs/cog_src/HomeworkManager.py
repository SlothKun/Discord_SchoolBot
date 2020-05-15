from .Homework import Homework
from .HomeworkMessage import HomeworkMessage

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

        # Channel collection elements
        self.chanCol = mDB[dbStructJson['db_collections']['channel']]
        self.chanFields = {
            'id': dbStructJson['db_collections']['channel_fields']['id'],
            'subject': dbStructJson['db_collections']['channel_fields']['subject'],
            'chanID': dbStructJson['db_collections']['channel_fields']['channelID']
        }

        # Subject collection elements
        self.subCol = mDB[dbStructJson['db_collections']['subject']]
        self.subjectList = []
        for sub in self.subCol.find({}, {dbStructJson['db_collections']['subject_fields']["id"]: 0, dbStructJson['db_collections']['subject_fields']["subjectName"]: 1}):
            self.subjectList.append(sub[dbStructJson['db_collections']['subject_fields']["subjectName"]].lower())

        # Emoji collection elements
        hmwEmojiCol = mDB[dbStructJson['db_collections']['emoji']]

        idField = dbStructJson['db_collections']['emoji_fields']['id']
        nameField = dbStructJson['db_collections']['emoji_fields']['name']
        valueField = dbStructJson['db_collections']['emoji_fields']['value']

        self.emojiNumber = [hmwEmojiCol.find_one({nameField: '0'}, {idField: 0, valueField:1})[valueField], hmwEmojiCol.find_one({nameField: '1'}, {idField: 0, valueField:1})[valueField]]

        self.emojiList = {
            HomeworkManager.HMW_EMOJIS[0] : hmwEmojiCol.find_one({nameField: 'back'}, {idField: 0, valueField: 1})[valueField],
            HomeworkManager.HMW_EMOJIS[1] : hmwEmojiCol.find_one({nameField: 'cross'}, {idField: 0, valueField: 1})[valueField],
            HomeworkManager.HMW_EMOJIS[2] : hmwEmojiCol.find_one({nameField: 'check'}, {idField: 0, valueField: 1})[valueField],
            HomeworkManager.HMW_EMOJIS[3] : hmwEmojiCol.find_one({nameField: 'confModif'}, {idField: 0, valueField: 1})[valueField],
            HomeworkManager.HMW_ACTIONS[0] : hmwEmojiCol.find_one({nameField: 'add'}, {idField: 0, valueField: 1})[valueField],
            HomeworkManager.HMW_ACTIONS[1] : hmwEmojiCol.find_one({nameField: 'edit'}, {idField: 0, valueField: 1})[valueField],
            HomeworkManager.HMW_ACTIONS[2] : hmwEmojiCol.find_one({nameField: 'delete'}, {idField: 0, valueField: 1})[valueField]
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
        try:
            hmw = self.homeworks[creatorID]
        except KeyError as ke:
            # Handling error when a user try to acces homeworks but have not been registered or shouldn't
            return None

        print(f"HOMEWORK_MAN - Observer called by hmw[{creatorID}]")
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
        try:
            currentHmw = self.homeworks[creatorID]
        except KeyError as ke:
            # Handling error when a user try to acces homeworks but have not been registered or shouldn't
            return False

        if (currentHmw.age > HomeworkManager.MAX_HMW_AGE):
            del currentHmw
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

    def listHmw(self, botAlteringUser):
        # Get all homework with a deadline greater than the current time
        homeworks = self.hmwCol.find({self.hmwFields['date']: {'$gte': datetime.utcnow()}}).sort(self.hmwFields['date'])
        emojis = [self.emojiList[HomeworkManager.HMW_ACTIONS[0]], self.emojiList[HomeworkManager.HMW_ACTIONS[1]], self.emojiList[HomeworkManager.HMW_ACTIONS[2]]]

        # Formatting the listing homework message before sending it
        formatedHmwList = HomeworkMessage.HMW_UTILS['formatingQuote']
        groupedHmw = self.groupHmwByDate(homeworks)
        for hmwDate in groupedHmw:
            formatedHmwList += f"\n{hmwDate}"
            for homework in groupedHmw[hmwDate]:
                formatedHmwList += f"\n\t- {homework[self.hmwFields['subject']]} : {homework[self.hmwFields['name']]}"
            formatedHmwList += "\n"

        if botAlteringUser:
            # Add this part to the message only if user is authorized to alter hmw (from the bot)
            formatedHmwList += HomeworkMessage.HMW_UTILS['separationLine']
            formatedHmwList += f"\n\t{emojis[0]} - Ajouter un devoir"
            formatedHmwList += f"\n\t{emojis[1]} - Éditer un devoir"
            formatedHmwList += f"\n\t{emojis[2]} - Supprimer un devoir"
        formatedHmwList += HomeworkMessage.HMW_UTILS['formatingQuote']

        return (formatedHmwList, emojis)

    def newHmw(self, creatorID, hmwAction, channelID, botMsgID):
        print(f"HOMEWORK_MAN - Creating a new homework for {creatorID} in mode {HomeworkManager.HMW_ACTIONS[hmwAction]}")
        suggestedSubject = self.chanCol.find_one({self.chanFields['chanID']: channelID})[self.chanFields['subject']]
        self.homeworks[creatorID] = Homework(creatorID, HomeworkManager.HMW_ACTIONS[hmwAction], self.hmwObserver, self.subjectList, suggestedSubject)
        self.linkedChannel[creatorID] = channelID
        self.linkedBotMsg[creatorID] = botMsgID

        emojiIDs = [HomeworkManager.HMW_EMOJIS[1]] # Cancel emoji
        msgBack = HomeworkMessage.HMW_ADD[self.homeworks[creatorID].state].substitute()
        (res, emojis) = self.formatBackMsg(self.homeworks[creatorID], emojiIDs, True, msgBack, True)
        return res

    def deleteHmw(self, creatorID, channelID):
        if self.checkHmw(creatorID, channelID):
            del self.homeworks[creatorID]
            del self.linkedChannel[creatorID]
            del self.linkedBotMsg[creatorID]
            return True
        return False

    def formatBackMsg(self, currentHmw, emojiIDs, updateRes, msgBack, beginStatus):
        emojis = []

        if currentHmw.isComplete:
            if not currentHmw.docAwaited and len(currentHmw.doc) <= 0:
                emojiIDs.append(HomeworkManager.HMW_EMOJIS[2])
            emojiIDs.append(HomeworkManager.HMW_EMOJIS[3])

        res = ""
        if not beginStatus:
            res = HomeworkMessage.diffFormatMsg(currentHmw.lastChange) + '\n'
            # res = HomeworkMessage.HMW_UTILS['formatingQuoteDiff']
            # res += currentHmw.lastChange
            # res += HomeworkMessage.HMW_UTILS['formatingQuote']
        res += HomeworkMessage.HMW_ADD['title'].substitute(stepNum = (currentHmw.stateIdx + 1), totalStep = currentHmw.nbStep)
        res += HomeworkMessage.stateDisplayer(currentHmw.stateIdx)
        res += HomeworkMessage.HMW_UTILS['formatingQuote']
        res += msgBack

        if not updateRes and currentHmw.state == Homework.HMW_STATES[currentHmw.userAction][4]:
            # IF the input subject is not correct but have some similarities within the DB
            for counter in range(0, len(currentHmw.subjectChoice)):
                choiceEmoji = self.emojiNumber[counter+1]
                emojis.append(choiceEmoji)
                res += HomeworkMessage.HMW_ADD['subjectChoiceReac'].substitute(reac = choiceEmoji, subject = currentHmw.subjectChoice[counter])

        res += HomeworkMessage.HMW_UTILS['separationLine']
        for emojiID in emojiIDs:
            res += HomeworkMessage.HMW_UTILS[emojiID].substitute(emoji = self.emojiList[emojiID], userAction = currentHmw.userActionName)
            emojis.append(self.emojiList[emojiID])
        res += HomeworkMessage.HMW_UTILS['formatingQuote']
        return (res, emojis)

    def updateHmw(self, creatorID, value, isBack = False):
        try:
            currentHmw = self.homeworks[creatorID]
        except KeyError as ke:
            # Handling error when a user try to acces homeworks but have not been registered or shouldn't
            return (None, None)

        emojiIDs = [HomeworkManager.HMW_EMOJIS[0], HomeworkManager.HMW_EMOJIS[1]]
        if not isBack:
            if not currentHmw.isComplete:
                # Send the new value to the corresponding homework
                # updateStatus = self.homeworks[creatorID].updateVal(value, isBack)
                (updateRes, msgBack) = currentHmw.updateVal(value, isBack)
                return self.formatBackMsg(currentHmw, emojiIDs, updateRes, msgBack, False)
            return (None, None)
        else:
            if currentHmw.isComplete:
                currentHmw.isComplete = False
            (updateRes, msgBack) = currentHmw.updateVal(value, isBack)
            return self.formatBackMsg(currentHmw, emojiIDs, updateRes, msgBack, False)

    def setHmwDoc(self, creatorID, msgAttachments):
        try:
            currentHmw = self.homeworks[creatorID]
        except KeyError as ke:
            # Handling error when a user try to acces homeworks but have not been registered or shouldn't
            return None
        print(f"HOMEWORKMANAGER - File to set: {msgAttachments[0].filename}")
        msgBack = currentHmw.updateDoc(msgAttachments)
        emojiIDs = [HomeworkManager.HMW_EMOJIS[0], HomeworkManager.HMW_EMOJIS[1]]
        return self.formatBackMsg(currentHmw, emojiIDs, True, msgBack, False)

    def setDocStatus(self, creatorID):
        try:
            currentHmw = self.homeworks[creatorID]
        except KeyError as ke:
            # Handling error when a user try to acces homeworks but have not been registered or shouldn't
            return None

        msgBack = currentHmw.updateDocStatus(True)
        if msgBack:
            emojiIDs = [HomeworkManager.HMW_EMOJIS[0], HomeworkManager.HMW_EMOJIS[1]]
            return self.formatBackMsg(currentHmw, emojiIDs, True, msgBack, False)
        else:
            return None
    
    def insertNewDict(self, creatorID, botAlteringUser):
        try:
            currentHmw = self.homeworks[creatorID]
        except KeyError as ke:
            # Handling error when a user try to acces homeworks but have not been registered or shouldn't
            return None
        
        hmwDict = currentHmw.hmwDict()

        chanID = self.chanCol.find_one({self.chanFields['subject']: hmwDict['subject']}, {self.chanFields['id']: 0, self.chanFields['chanID']: 1})[self.chanFields['chanID']]

        self.hmwCol.insert_one(hmwDict)

        res = HomeworkMessage.HMW_CONF['dbUpdated'].substitute()
        (listHmw, emojis) = self.listHmw(botAlteringUser)
        res += listHmw

        return (res, emojis, chanID, currentHmw.doc)

    def correctSubVal(self, creatorID, voteIdx):
        try:
            currentHmw =  self.homeworks[creatorID]
        except KeyError as ke:
            # Handling error when a user try to acces homeworks but have not been registered or shouldn't
            return None

        msgBack = currentHmw.setNewSubjectVal(voteIdx - 1) # (- 1) because the emoji is 1 instead of 0
        emojiIDs = [HomeworkManager.HMW_EMOJIS[0], HomeworkManager.HMW_EMOJIS[1]]
        return self.formatBackMsg(currentHmw, emojiIDs, True, msgBack, False)