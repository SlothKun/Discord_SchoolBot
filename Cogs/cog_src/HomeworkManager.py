from .Homework import Homework
from .HomeworkMessage import HomeworkMessage

from string import Template
from datetime import datetime

class HomeworkManager():

    HMW_ACTIONS = ["hmwAdd", "hmwEdit", "hmwDelete"]
    HMW_EMOJIS = ["back", "cancel", "addFile", "modifConf", "nextElemsInDB"]
    MAX_HMW_AGE = 600 #Maximum age for an homework (in seconds)

    def __init__(self, dbStructJson, mDB):
        self._homeworks = {}
        self._linkedChannel = {}
        self._linkedBotMsg = {}
        self._actionMsgDict = {}
        self._suggestedSubject = {}
        self._hmwToList = {}
        self._numberedHmwList = {}

        # Homework collection elements
        self.hmwCol = mDB[dbStructJson['db_collections']['homework']]
        self.hmwFields = {
            'date': dbStructJson['db_collections']['homework_fields']['deadline'],
            'subject': dbStructJson['db_collections']['homework_fields']['subject'],
            'name': dbStructJson['db_collections']['homework_fields']['name'],
            'chanID': dbStructJson['db_collections']['homework_fields']['chanID']
        }

        # Channel collection elements
        self.chanCol = mDB[dbStructJson['db_collections']['channel']]
        self.chanFields = {
            'id': dbStructJson['db_collections']['channel_fields']['id'],
            'subject': dbStructJson['db_collections']['channel_fields']['subject'],
            'chanID': dbStructJson['db_collections']['channel_fields']['channelID'],
            'chanName': dbStructJson['db_collections']['channel_fields']['channelName'],
            'catName': dbStructJson['db_collections']['channel_fields']['categoryName']
        }

        # Subject collection elements
        self.subCol = mDB[dbStructJson['db_collections']['subject']]
        self.subjectList = []
        for sub in self.subCol.find({}, {dbStructJson['db_collections']['subject_fields']["id"]: 0, dbStructJson['db_collections']['subject_fields']["subjectName"]: 1}):
            self.subjectList.append(sub[dbStructJson['db_collections']['subject_fields']["subjectName"]].lower())

        # Emoji collection elements
        self.hmwEmojiCol = mDB[dbStructJson['db_collections']['emoji']]
        self.emojiFields = {
            'id': dbStructJson['db_collections']['emoji_fields']['id'],
            'name': dbStructJson['db_collections']['emoji_fields']['name'],
            'value': dbStructJson['db_collections']['emoji_fields']['value']
        }
        self.emojiNumber = [self.hmwEmojiCol.find_one({self.emojiFields['name']: str(a)}, {self.emojiFields['id']: 0, self.emojiFields['value']:1})[self.emojiFields['value']] for a in range(0,9)]
        self.emojiList = {
            HomeworkManager.HMW_EMOJIS[0] : self.hmwEmojiCol.find_one({self.emojiFields['name']: 'back'}, {self.emojiFields['id']: 0, self.emojiFields['value']: 1})[self.emojiFields['value']],
            HomeworkManager.HMW_EMOJIS[1] : self.hmwEmojiCol.find_one({self.emojiFields['name']: 'cross'}, {self.emojiFields['id']: 0, self.emojiFields['value']: 1})[self.emojiFields['value']],
            HomeworkManager.HMW_EMOJIS[2] : self.hmwEmojiCol.find_one({self.emojiFields['name']: 'check'}, {self.emojiFields['id']: 0, self.emojiFields['value']: 1})[self.emojiFields['value']],
            HomeworkManager.HMW_EMOJIS[3] : self.hmwEmojiCol.find_one({self.emojiFields['name']: 'confModif'}, {self.emojiFields['id']: 0, self.emojiFields['value']: 1})[self.emojiFields['value']],
            HomeworkManager.HMW_EMOJIS[4] : self.hmwEmojiCol.find_one({self.emojiFields['name']: 'nextElem'}, {self.emojiFields['id']: 0, self.emojiFields['value']: 1})[self.emojiFields['value']],
            HomeworkManager.HMW_ACTIONS[0] : self.hmwEmojiCol.find_one({self.emojiFields['name']: 'add'}, {self.emojiFields['id']: 0, self.emojiFields['value']: 1})[self.emojiFields['value']],
            HomeworkManager.HMW_ACTIONS[1] : self.hmwEmojiCol.find_one({self.emojiFields['name']: 'edit'}, {self.emojiFields['id']: 0, self.emojiFields['value']: 1})[self.emojiFields['value']],
            HomeworkManager.HMW_ACTIONS[2] : self.hmwEmojiCol.find_one({self.emojiFields['name']: 'delete'}, {self.emojiFields['id']: 0, self.emojiFields['value']: 1})[self.emojiFields['value']]
        }
    
    def __str__(self):
        res =  f"HomeworkManager currently keep track of {len(self.homeworks)} homework(s):"
        for hmw in self.homeworks:
            res += f"\n\t{hmw.id} - {hmw.name} in {hmw.userAction} mode"
        return res

    ##########
    ##########
    ## GETTERs
    ##########
    ##########

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
    def actionMsgDict(self):
        return self._actionMsgDict

    @property
    def hmwToList(self):
        return self._hmwToList

    @property
    def numberedHmwList(self):
        return self._numberedHmwList

    @property
    def docBotMsg(self):
        return self._docBotMsg

    @property
    def suggestedSubject(self):
        return self._suggestedSubject

    ##########
    ##########
    ## UTILITY FUNCTIONs
    ##########
    ##########

    def hmwObserver(self, creatorID, number = -1):
        try:
            currentHmw = self.homeworks[creatorID]
        except KeyError as ke:
            # Handling error when a user try to acces homeworks but have not been registered or shouldn't
            return False

        if currentHmw.userAction == HomeworkManager.HMW_ACTIONS[0]:
            if currentHmw.state == Homework.HMW_STATES[1]:
                # Target homework in state 'name'
                # Set the suggested subject for target homework (based on channel used for the command)
                self.suggestedSubject[creatorID] = not self.suggestedSubject[creatorID]
            elif currentHmw.state == Homework.HMW_STATES[2]:
                # Target homework in state 'subject'
                # Check if the new homework is unique (based on tuple (name, subject))
                utcDate = datetime.utcnow()
                thisDay = datetime(utcDate.year, utcDate.month, utcDate.day)
                anyHmw = self.hmwCol.find_one({self.hmwFields['name']: currentHmw.name, self.hmwFields['subject']: currentHmw.subject, self.hmwFields['date']: {'$gte': thisDay}})
                if anyHmw:
                    # There already is an homework with this name and subject in collection
                    currentHmw.inDB = True
                    anyHmwStr = HomeworkMessage.HMW_DESC['global'].substitute(subject = anyHmw[self.hmwFields['subject']], nom = anyHmw[self.hmwFields['name']], status = None, date = anyHmw[self.hmwFields['date']])
                    currentHmw.lastChange = HomeworkMessage.HMW_CONF['inDB'].substitute(inDBHmw = anyHmwStr)
                    
                    # Two reverse update to go back to 'name' state
                    currentHmw.updateState(True)
                    currentHmw.updateState(True)
                else:
                    # No similar homework --> everything is fine
                    currentHmw.inDB = False
                    oldChange = currentHmw.lastChange
                    if len(oldChange) == 0:
                        currentHmw.lastChange = HomeworkMessage.HMW_CONF['goodDB'].substitute(nameVar = currentHmw.name, subjectVar = currentHmw.subject)
                    else:
                        for change in oldChange:
                            currentHmw.lastChange = change
        elif currentHmw.userAction == HomeworkManager.HMW_ACTIONS[1]:
            # HMW_EDIT
            pass
        elif currentHmw.userAction == HomeworkManager.HMW_ACTIONS[2]:
            # HMW_DELETE
            if currentHmw.state == Homework.HMW_STATES[2]:
                # Subject
                self.hmwToList[creatorID] = not self.hmwToList[creatorID]
                if number >= 0:
                    currentHmw.selectedSubject = self.numberedHmwList[creatorID][number]

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
        dateRes = {}
        for hmw in hmwList:
            hmwDate = hmw[self.hmwFields['date']].strftime('%d %B')
            if hmwDate in dateRes:
                dateRes[hmwDate].append(hmw)
            else:
                dateRes[hmwDate] = [hmw]
        return dateRes

    def groupHmw(self, hmwList):
        dateRes = self.groupHmwByDate(hmwList)
        
        finalRes = {}
        for hmwDate in dateRes:
            finalRes[hmwDate] = {}
            for hmw in dateRes[hmwDate]:
                if hmw[self.hmwFields['subject']] in finalRes[hmwDate]:
                    finalRes[hmwDate][hmw[self.hmwFields['subject']]].append(hmw)
                else:
                    finalRes[hmwDate][hmw[self.hmwFields['subject']]] = [hmw]
        return finalRes

    def listHmw(self, botAlteringUser):
        # Get all homework with a deadline greater than the current time
        utcDate = datetime.utcnow()
        thisDay = datetime(utcDate.year, utcDate.month, utcDate.day)
        homeworks = self.hmwCol.find({self.hmwFields['date']: {'$gte': thisDay}}).sort(self.hmwFields['date'])
        emojis = []

        # Formatting the listing homework message before sending it
        formatedHmwList = HomeworkMessage.HMW_UTILS['formatingQuote']
        groupedHmw = self.groupHmw(homeworks)
        for hmwDate in groupedHmw:
            formatedHmwList += f"\nPour le {hmwDate} :"
            for subject in groupedHmw[hmwDate]:
                formatedHmwList += f"\n\t* {subject} :"
                for homework in groupedHmw[hmwDate][subject]:
                    if homework[self.hmwFields['chanID']]:
                        formatedHmwList += f"\n\t\t * {homework[self.hmwFields['name']]} ({homework[self.hmwFields['chanID']]})"
                    else:
                        formatedHmwList += f"\n\t\t * {homework[self.hmwFields['name']]}"
            formatedHmwList += "\n"

        if botAlteringUser:
            # Add this part to the message only if user is authorized to alter hmw (from the bot)
            # emojis = [self.emojiList[HomeworkManager.HMW_ACTIONS[0]], self.emojiList[HomeworkManager.HMW_ACTIONS[1]], self.emojiList[HomeworkManager.HMW_ACTIONS[2]]]
            emojis = [self.emojiList[HomeworkManager.HMW_ACTIONS[0]], self.emojiList[HomeworkManager.HMW_ACTIONS[2]]]

            formatedHmwList += HomeworkMessage.HMW_UTILS['separationLine']
            formatedHmwList += f"\n\t{emojis[0]} - Ajouter un devoir"
            # formatedHmwList += f"\n\t{emojis[1]} - Éditer un devoir"
            formatedHmwList += f"\n\t{emojis[1]} - Supprimer un devoir"
        formatedHmwList += HomeworkMessage.HMW_UTILS['formatingQuote']

        return (formatedHmwList, emojis)

    def listHmwBySubject(self, creatorID, minIdx = 0):
        currentHmw = self.homeworks[creatorID]

        utcDate = datetime.utcnow()
        thisDay = datetime(utcDate.year, utcDate.month, utcDate.day)
        homeworks = self.hmwCol.find({self.hmwFields['subject']: currentHmw.subject, self.hmwFields['date']: {'$gte': thisDay}}).sort(self.hmwFields['date'])
        nbRes = self.hmwCol.count_documents({self.hmwFields['subject']: currentHmw.subject, self.hmwFields['date']: {'$gte': thisDay}})
        emojis = []

        datedHmw = self.groupHmwByDate(homeworks)
        formatedHmwList = f"* {currentHmw.subject}"
        counter = 0
        for hmwDate in datedHmw:
            if (counter >= minIdx and counter < (minIdx + 10)) :
                formatedHmwList += f"\n\t* {hmwDate} :"
                for hmw in datedHmw[hmwDate]:
                    if (counter < (minIdx + 10)):
                        emoji = self.emojiNumber[(counter - minIdx)]
                        formatedHmwList += f"\n\t\t* {hmw[self.hmwFields['name']]} --> {emoji}"
                        emojis.append(emoji)
                        counter += 1
                        self.numberedHmwList[creatorID].append(hmw)
                    else:
                        break
            elif (counter < minIdx):
                counter += 1
            else:
                break

        if counter < (nbRes - 1):
            currentHmw.moreDocInDB = True
        else:
            currentHmw.moreDocInDB = False
        return (formatedHmwList, emojis)

    def newHmw(self, creatorID, hmwAction, channelID, botMsgID):
        print(f"HOMEWORK_MAN - Creating a new homework for {creatorID} in mode {HomeworkManager.HMW_ACTIONS[hmwAction]}")
        suggestedSubject = self.chanCol.find_one({self.chanFields['chanID']: str(channelID)})[self.chanFields['subject']]

        self.homeworks[creatorID] = Homework(creatorID, HomeworkManager.HMW_ACTIONS[hmwAction], self.hmwObserver, self.subjectList, suggestedSubject)

        self.linkedChannel[creatorID] = channelID
        self.linkedBotMsg[creatorID] = botMsgID
        self.suggestedSubject[creatorID] = False
        self.hmwToList[creatorID] = False
        self.numberedHmwList[creatorID] = []

        emojiIDs = [HomeworkManager.HMW_EMOJIS[1]] # Cancel emoji
        if HomeworkManager.HMW_ACTIONS[hmwAction] == "hmwAdd":
            self.actionMsgDict[creatorID] = HomeworkMessage.HMW_ADD
            msgBack = HomeworkMessage.HMW_ADD[self.homeworks[creatorID].state].substitute()
        elif HomeworkManager.HMW_ACTIONS[hmwAction] == "hmwEdit":
            self.actionMsgDict[creatorID] = HomeworkMessage.HMW_EDIT
            msgBack = HomeworkMessage.HMW_EDIT[self.homeworks[creatorID].state].substitute()
        elif HomeworkManager.HMW_ACTIONS[hmwAction] == "hmwDelete":
            self.actionMsgDict[creatorID] = HomeworkMessage.HMW_DELETE
            msgBack = HomeworkMessage.HMW_DELETE[self.homeworks[creatorID].state].substitute()
            self.suggestedSubject[creatorID] = True
        return self.formatBackMsg(self.homeworks[creatorID], self.suggestedSubject[creatorID], self.actionMsgDict[creatorID], emojiIDs, True, msgBack, True, self.homeworks[creatorID].moreDocInDB)

    def deleteHmw(self, creatorID, channelID):
        if self.checkHmw(creatorID, channelID):
            del self.homeworks[creatorID]
            del self.linkedChannel[creatorID]
            del self.linkedBotMsg[creatorID]
            return (True, HomeworkMessage.diffFormatMsg(HomeworkMessage.HMW_CONF['hmwDeleted'].substitute()))
        return (False, None)

    def formatBackMsg(self, currentHmw, suggestedSubject, actionMsgDict, emojiIDs, updateRes, msgBack, beginStatus, moreInDBStatus):
        emojis = []

        if currentHmw.isComplete:
            if (currentHmw.userAction == HomeworkManager.HMW_ACTIONS[0] and not currentHmw.docAwaited and len(currentHmw.doc) <= 0):
                emojiIDs.append(HomeworkManager.HMW_EMOJIS[2])
            emojiIDs.append(HomeworkManager.HMW_EMOJIS[3])

        if moreInDBStatus:
            emojiIDs.append(HomeworkManager.HMW_EMOJIS[4])

        res = ""
        if not beginStatus:
            oldChange = currentHmw.lastChange
            # print(f"HOMEWORK_MAN - FormatBackMsg - oldChange: {oldChange}")
            for hmwChange in oldChange:
                # print(f"HOMEWORK_MAN - FormatBackMsg - hmwChange: {hmwChange}")
                res += HomeworkMessage.diffFormatMsg(hmwChange)
            res += '\n'
        res += actionMsgDict['title'].substitute(stepNum = (currentHmw.stateIdx + 1), totalStep = currentHmw.nbStep)
        res += HomeworkMessage.stateDisplayer(currentHmw.userAction, currentHmw.stateIdx)
        res += HomeworkMessage.HMW_UTILS['formatingQuote']
        res += msgBack

        if not updateRes:
            if (
                currentHmw.state == Homework.HMW_STATES[2] and # Homework in state 'subject'
                (currentHmw.userAction == HomeworkManager.HMW_ACTIONS[0] or currentHmw.userAction == HomeworkManager.HMW_ACTIONS[2]) # Homework in HMW_ADD or HMW_DELETE
               ):
                # IF the input subject is not correct but have some similarities within the DB
                for counter in range(1, len(currentHmw.subjectChoice) + 1):
                    choiceEmoji = self.emojiNumber[counter]
                    emojis.append(choiceEmoji)
                    res += HomeworkMessage.HMW_UTILS['subjectChoiceReac'].substitute(reac = choiceEmoji, subject = currentHmw.subjectChoice[counter])
        if suggestedSubject:
            # Suggested subject will be required in next user message
            if ( 
                (currentHmw.userAction == HomeworkManager.HMW_ACTIONS[0] and currentHmw.state == Homework.HMW_STATES[1]) or # Homework in HMW_ADD and state 'name'
                (currentHmw.userAction == HomeworkManager.HMW_ACTIONS[1] and currentHmw.state == Homework.HMW_STATES[0]) or # Homework in HMW_EDIT and state 'idle'
                (currentHmw.userAction == HomeworkManager.HMW_ACTIONS[2] and currentHmw.state == Homework.HMW_STATES[0])    # Homework in HMW_DELETE and state 'idle'
               ):
                subEmoji = self.emojiNumber[1] # Emoji #1
                emojis.append(subEmoji)
                res += HomeworkMessage.HMW_UTILS['subjectChoiceReac'].substitute(reac = subEmoji, subject = currentHmw.suggSubject)

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
                (updateRes, msgBack) = currentHmw.updateVal(value, isBack)

                hmwEmojis = []
                if currentHmw.inDB:
                    msgBack = HomeworkMessage.HMW_UTILS['inDB'].substitute(oldName = currentHmw.name)
                if currentHmw.userAction == HomeworkManager.HMW_ACTIONS[2]:
                    ##### HMW_DELETE
                    (hmwList, hmwEmojis) = self.listHmwBySubject(creatorID)
                    msgBack = self.actionMsgDict[creatorID][currentHmw.state].substitute(hmwList = hmwList)
                    currentHmw.hmwPageIdx += 1

                (res, emojis) = self.formatBackMsg(currentHmw, self.suggestedSubject[creatorID], self.actionMsgDict[creatorID], emojiIDs, updateRes, msgBack, False, currentHmw.moreDocInDB)
                emojis = emojis + hmwEmojis
                return (res, emojis)
            return (None, None)
        else:
            if currentHmw.isComplete:
                currentHmw.isComplete = False
            (updateRes, msgBack) = currentHmw.updateVal(value, isBack)
            return self.formatBackMsg(currentHmw, self.suggestedSubject[creatorID], self.actionMsgDict[creatorID], emojiIDs, updateRes, msgBack, False, currentHmw.moreDocInDB)

    def setHmwDoc(self, creatorID, msgAttachments):
        try:
            currentHmw = self.homeworks[creatorID]
        except KeyError as ke:
            # Handling error when a user try to acces homeworks but have not been registered or shouldn't
            return None
        msgBack = currentHmw.updateDoc(msgAttachments)
        emojiIDs = [HomeworkManager.HMW_EMOJIS[0], HomeworkManager.HMW_EMOJIS[1]]
        return self.formatBackMsg(currentHmw, self.suggestedSubject[creatorID], self.actionMsgDict[creatorID], emojiIDs, True, msgBack, False, currentHmw.moreDocInDB)

    def checkedHomework(self, creatorID):
        try:
            currentHmw = self.homeworks[creatorID]
        except KeyError as ke:
            # Handling error when a user try to acces homeworks but have not been registered or shouldn't
            return None

        if currentHmw.userAction == HomeworkManager.HMW_ACTIONS[0]:
            #HMW_ADD
            msgBack = currentHmw.updateDocStatus(True)
            if msgBack:
                emojiIDs = [HomeworkManager.HMW_EMOJIS[0], HomeworkManager.HMW_EMOJIS[1]]
                return self.formatBackMsg(currentHmw, self.suggestedSubject[creatorID], self.actionMsgDict[creatorID], emojiIDs, True, msgBack, False, currentHmw.moreDocInDB)
            else:
                return None
        
        elif currentHmw.userAction == HomeworkManager.HMW_ACTIONS[1]:
            #HMW_EDIT
            pass

        elif currentHmw.userAction == HomeworkManager.HMW_ACTIONS[0]:
            #HMW_DELETE
            # User is validating the homework selected to delete
            pass
    
    def validateHmwChange(self, creatorID):
        try:
            currentHmw = self.homeworks[creatorID]
        except KeyError as ke:
            # Handling error when a user try to acces homeworks but have not been registered or shouldn't
            return None

        chanID = None
        docs = None
        res = ''
        emojis = []
        if currentHmw.userAction == HomeworkManager.HMW_ACTIONS[0]:
            # HMW_ADD
            if len(currentHmw.doc) > 0:
                docChan = self.chanCol.find_one({self.chanFields['subject']: currentHmw.subject, self.chanFields['catName']: 'documents'})
                chanID = docChan[self.chanFields['chanID']]
                currentHmw.dedicatedChanID = docChan[self.chanFields['chanName']]
                docs = currentHmw.doc
            hmwDict = currentHmw.hmwDict()
            self.hmwCol.insert_one(hmwDict)

            res = HomeworkMessage.diffFormatMsg(HomeworkMessage.HMW_CONF['hmwAddedInDB'].substitute())
            (listHmw, emojis) = self.listHmw(False)
            res += listHmw
        elif currentHmw.userAction == HomeworkManager.HMW_ACTIONS[1]:
            # HMW_EDIT
            pass
        elif currentHmw.userAction == HomeworkManager.HMW_ACTIONS[2]:
            # HMW_DELETE
            self.hmwCol.delete_one({self.hmwFields['subject']: currentHmw.selectedSubject['subject'], self.hmwFields['name']: currentHmw.selectedSubject['name']})
            res = HomeworkMessage.diffFormatMsg(HomeworkMessage.HMW_CONF['hmwDeletedInDB'].substitute())

        return (res, emojis, chanID, docs)

    def numberedAction(self, creatorID, voteIdx):
        try:
            currentHmw =  self.homeworks[creatorID]
        except KeyError as ke:
            # Handling error when a user try to acces homeworks but have not been registered or shouldn't
            return None

        emojiIDs = [HomeworkManager.HMW_EMOJIS[0], HomeworkManager.HMW_EMOJIS[1]] # [back, cancel]
        if currentHmw.userAction == HomeworkManager.HMW_ACTIONS[0]:
            # HMW_ADD
            msgBack = currentHmw.numberedAddAction(voteIdx - 1) # (- 1) because the emoji is 1 instead of 0
            if currentHmw.inDB:
                msgBack = HomeworkMessage.HMW_UTILS['inDB'].substitute(oldName = currentHmw.name)
            return self.formatBackMsg(currentHmw, self.suggestedSubject[creatorID], self.actionMsgDict[creatorID], emojiIDs, True, msgBack, False, currentHmw.moreDocInDB)

        elif currentHmw.userAction == HomeworkManager.HMW_ACTIONS[1]:
            # HMW_EDIT
            pass

        elif currentHmw.userAction == HomeworkManager.HMW_ACTIONS[2]:
            # HMW_DELETE
            msgBack = currentHmw.numberedDeleteAction(voteIdx - 1)
            if currentHmw.state == Homework.HMW_STATES[2]:
                # Homework in state 'subject'
                (hmwList, hmwEmojis) = self.listHmwBySubject(creatorID)
                msgBack = self.actionMsgDict[creatorID][currentHmw.state].substitute(hmwList = hmwList)
                currentHmw.hmwPageIdx += 1
                (res, emojis) = self.formatBackMsg(currentHmw, self.suggestedSubject[creatorID], self.actionMsgDict[creatorID], emojiIDs, True, msgBack, False, currentHmw.moreDocInDB)
                emojis = emojis + hmwEmojis
                return (res, emojis)
            elif currentHmw.state == Homework.HMW_STATES[1]:
                # Homework in state 'name'
                pass
            return self.formatBackMsg(currentHmw, self.suggestedSubject[creatorID], self.actionMsgDict[creatorID], emojiIDs, True, msgBack, False, currentHmw.moreDocInDB)
        else:
            # Possible error --> To catch
            pass

    def refreshHmwList(self, creatorID):
        currentHmw = self.homeworks[creatorID]
        emojiIDs = [HomeworkManager.HMW_EMOJIS[0], HomeworkManager.HMW_EMOJIS[1]]

        (hmwList, hmwEmojis) = self.listHmwBySubject(creatorID, 10 * currentHmw.hmwPageIdx)
        msgBack = self.actionMsgDict[creatorID][currentHmw.state].substitute(hmwList = hmwList)
        currentHmw.hmwPageIdx += 1
        (res, emojis) = self.formatBackMsg(currentHmw, self.suggestedSubject[creatorID], self.actionMsgDict[creatorID], emojiIDs, True, msgBack, False, currentHmw.moreDocInDB)
        emojis = emojis + hmwEmojis
        return (res, emojis)
