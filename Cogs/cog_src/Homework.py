from .HomeworkMessage import HomeworkMessage

import datetime

from string import Template
from difflib import get_close_matches

class Homework():

    HMW_USER_ACTION = ["hmwAdd", "hmwEdit", "hmwDelete"]
    HMW_UA_FR = {
        HMW_USER_ACTION[0]: "ajout",
        HMW_USER_ACTION[1]: "édition",
        HMW_USER_ACTION[2]: "suppression"
    }

    HMW_STATES = ['idle', 'name', 'subject', 'date', 'status', 'document', 'partToEdit']

    HMW_STATES_SEQ = {
        HMW_USER_ACTION[0] : [HMW_STATES[0], HMW_STATES[1], HMW_STATES[2], HMW_STATES[3], HMW_STATES[4], HMW_STATES[5]],
        HMW_USER_ACTION[1] : [HMW_STATES[0], HMW_STATES[2], HMW_STATES[1], HMW_STATES[6]],
        HMW_USER_ACTION[2] : [HMW_STATES[0], HMW_STATES[2], HMW_STATES[1]]
    }

    HMW_ACTION_MSG_DIC = {
        HMW_USER_ACTION[0] : HomeworkMessage.HMW_ADD,
        HMW_USER_ACTION[1] : HomeworkMessage.HMW_EDIT,
        HMW_USER_ACTION[2] : HomeworkMessage.HMW_DELETE,
    }

    DATE_FORMAT = {
        'datetime': '%d/%m',
        'str': 'JJ/MM',
        'strptime': '%Y/%d/%m'
    }

    WORD_SENSIBILITY = 0.4
    NAME_MAX_LENGTH = 21

    def __init__(self, creator, userAction, observerFunc, subjectList, suggSubject):
        self._creator = creator
        self._creationDate = datetime.datetime.utcnow()
        self._suggestedSubject = suggSubject
        self._selectedSubject = None
        self._observer = observerFunc

        self._userAction = userAction
        self._state = Homework.HMW_STATES[0]
        self._lastChange = []
        self._lastError = ""
        self._inDB = False
        self._moreDocInDB = False
        self._isComplete = False
        self._hmwPageIdx = 0

        self._name = ""
        self._docAwaited = False
        self._doc = []
        self._dedicatedChanID = None
        self._deadline = None
        self._status = None
        self._subject = None

        self.lastDeletedDoc = ''

        self.subjectDBList = subjectList
        self.subjectChoice = []

    def __str__(self):
        desc = HomeworkMessage.HMW_DESC['global'].substitute(subject = self.subject, nom = self.name, status = self.status, date = self.date.strftime('%d %B %Y'))
        if len(self.doc) > 0:
            if len(self.doc) > 1:
                desc += HomeworkMessage.HMW_DESC['docList'].substitute(nbDoc = len(self.doc), plural = 's')
            else:
                desc += HomeworkMessage.HMW_DESC['docList'].substitute(nbDoc = len(self.doc), plural = '')
            for doc in self.doc:
                desc +=  HomeworkMessage.HMW_DESC['docName'].substitute(docName = doc.filename)
        else:
            desc += HomeworkMessage.HMW_DESC['docSuggestion'].substitute()
        return desc

    def hmwDict(self):
        hmwDict = {}
        hmwDict['name'] = self.name
        hmwDict['publish_date'] = self._creationDate
        hmwDict['deadline'] = self.date
        hmwDict['creator'] = {'name': self.id}
        hmwDict['subject'] = self.subject
        hmwDict['cible'] = 'TS1'
        hmwDict['docChanID'] = self.dedicatedChanID
        hmwDict['status'] = self.status
        return hmwDict

    ##########
    ##########
    ## GETTERs
    ##########
    ##########

    @property
    def id(self):
        return self._creator
    
    @property
    def age(self):
        return (datetime.datetime.utcnow() - self._creationDate).total_seconds()

    @property
    def suggSubject(self):
        return self._suggestedSubject

    @property
    def selectedSubject(self):
        return self._selectedSubject

    @property
    def userAction(self):
        return self._userAction

    @property
    def userActionName(self):
        return Homework.HMW_UA_FR[self.userAction]

    @property
    def state(self):
        return self._state

    @property
    def stateIdx(self):
        return Homework.HMW_STATES_SEQ[self.userAction].index(self.state)

    @property
    def lastError(self):
        return self._lastError

    @property
    def lastChange(self):
        temp = self._lastChange
        self._lastChange = []
        return temp

    @property
    def inDB(self):
        return self._inDB

    @property
    def moreDocInDB(self):
        return self._moreDocInDB

    @property
    def isComplete(self):
        return self._isComplete

    @property
    def hmwPageIdx(self):
        return self._hmwPageIdx

    @property
    def name(self):
        return self._name

    @property
    def docAwaited(self):
        return self._docAwaited

    @property
    def doc(self):
        return self._doc

    @property
    def dedicatedChanID(self):
        return self._dedicatedChanID
    
    @property
    def date(self):
        return self._deadline
    
    @property
    def status(self):
        return self._status
    
    @property
    def subject(self):
        return self._subject

    @property
    def nbStep(self):
        if not self.docAwaited:
            return len(Homework.HMW_STATES_SEQ[self.userAction]) - 1
        return len(Homework.HMW_STATES_SEQ[self.userAction])

    ##########
    ########## 
    ## SETTERs
    ##########
    ##########

    @selectedSubject.setter
    def selectedSubject(self, value):
        self._selectedSubject = value

    @userAction.setter
    def userAction(self, value):
        self._userAction = value
        
    @state.setter
    def state(self, value):
        self._state = value
        print(f"HOMEWORK - Hmw now in state {self.state}")

    @lastError.setter
    def lastError(self, value):
        self._lastError = value

    @lastChange.setter
    def lastChange(self, value):
        self._lastChange.append(value)

    @inDB.setter
    def inDB(self, value):
        self._inDB = value

    @moreDocInDB.setter
    def moreDocInDB(self, value):
        self._moreDocInDB = value

    @isComplete.setter
    def isComplete(self, value):
        self._isComplete = value

    @hmwPageIdx.setter
    def hmwPageIdx(self, value):
        self._hmwPageIdx = value

    @name.setter
    def name(self, value):
        self._name = value
    
    @docAwaited.setter
    def docAwaited(self, value):
        self._docAwaited = value
    
    @doc.setter
    def doc(self, value):
        self._doc.append(value)

    @dedicatedChanID.setter
    def dedicatedChanID(self, value):
        self._dedicatedChanID = value
    
    @date.setter
    def date(self, value):
        self._deadline = value
    
    @status.setter
    def status(self, value):
        self._status = value
    
    @subject.setter
    def subject(self, value):
        self._subject = value

    ##########
    ##########
    ## UTILITY FUNCTIONs
    ##########
    ##########

    def nameCheck(self, res, value):
        pass

    def dateComparer(self, date1, date2):
        if date1.year < date2.year:
            return True
        elif date1.year == date2.year:
            if date1.month < date2.month:
                return True
            elif date1.month == date2.month:
                if date1.day <= date2.day:
                    return True
        return False

    def dateCheck(self, res, value):
        try:
            value = str(datetime.datetime.now().year) + '/' + value
            newDate = datetime.datetime.strptime(value, Homework.DATE_FORMAT['strptime'])
            if self.dateComparer(datetime.datetime.utcnow(), newDate):
                self.date = newDate
                res = res.substitute()
                return (True, res)
            else:
                self.lastError = HomeworkMessage.HMW_CONF['dateInf'].substitute()
                self.lastChange = HomeworkMessage.HMW_CONF["wrongAction"].substitute(errorMsg = self.lastError)
                self.date = None
                self.updateState(True)
                res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state].substitute(dateFormat = Homework.DATE_FORMAT['str'], dateExample = datetime.datetime.now().strftime(Homework.DATE_FORMAT['datetime']))
                return (False, res)
            
        except ValueError as ve:
            self.lastError = HomeworkMessage.HMW_CONF['dateError'].substitute(dateFormat = Homework.DATE_FORMAT['str'], date = datetime.datetime.now().strftime(Homework.DATE_FORMAT['datetime']))
            self.lastChange = HomeworkMessage.HMW_CONF["wrongAction"].substitute(errorMsg = self.lastError)
            self.date = None
            self.updateState(True)
            res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state].substitute(dateFormat = Homework.DATE_FORMAT['str'], dateExample = datetime.datetime.now().strftime(Homework.DATE_FORMAT['datetime']))
            return (False, res)

    def updateState(self, isBack):
        # Function to update the state of the current homework forward or backward if needed
        if isBack:
            if self.state == Homework.HMW_STATES[5]:
                #Document
                if len(self.doc) > 0:
                    self.lastDeletedDoc = self.doc[-1].filename
                    del self.doc[-1]
                else:
                    # No more docs, switch back to previous state (status)
                    self.state = Homework.HMW_STATES_SEQ[self.userAction][max(0, self.stateIdx - 1)]
            else:
                self.state = Homework.HMW_STATES_SEQ[self.userAction][max(0, self.stateIdx - 1)]
        else:
            self.state = Homework.HMW_STATES_SEQ[self.userAction][min((len(Homework.HMW_STATES_SEQ[self.userAction]) - 1), self.stateIdx + 1)]
    
    def updateVal(self, value, isBack):
        res = None
        updateRes = True
        emojis = []
        if isBack:
            # Canceling last modification
            if self.userAction == Homework.HMW_USER_ACTION[0]:
                ##### HMW_ADD
                self.updateState(isBack)
                res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state]
                confMsg = 'cancelledAction'
                oldValue = ""
                if self.state == Homework.HMW_STATES[0]:
                    #Idle
                    oldValue = self.name
                    # self.name = None
                    res = res.substitute()
                elif self.state == Homework.HMW_STATES[1]:
                    #name
                    oldValue = self.subject
                    res = res.substitute()
                elif self.state == Homework.HMW_STATES[2]:
                    #Subject
                    oldValue = self.date.strftime(Homework.DATE_FORMAT['datetime'])
                    # self.date = None
                    res = res.substitute(dateFormat = Homework.DATE_FORMAT['str'], dateExample = datetime.datetime.now().strftime(Homework.DATE_FORMAT['datetime']))
                elif self.state == Homework.HMW_STATES[3]:
                    #Date
                    oldValue = self.status
                    # self.status = None
                    res = res.substitute()
                elif self.state == Homework.HMW_STATES[4]:
                    #Status
                    self.isComplete = True
                    confMsg = 'cancelledDoc'
                    oldValue = None
                    self.docAwaited = False
                    # self.subject = None
                    res = res.substitute(hmwRecap = self)
                elif self.state == Homework.HMW_STATES[5]:
                    #Document
                    self.isComplete = True
                    oldValue = self.lastDeletedDoc
                    res = res.substitute(hmwRecap = self)
                self.lastChange = HomeworkMessage.HMW_CONF[confMsg].substitute(oldVal = oldValue)

            elif self.userAction == Homework.HMW_USER_ACTION[1]:
                ##### EDIT
                pass

            elif self.userAction == Homework.HMW_USER_ACTION[2]:
                ##### DELETE
                pass
        else:
            self.updateState(isBack)
            res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state]
            if self.userAction == Homework.HMW_USER_ACTION[0]:
                ##### HMW_ADD
                if self.state == Homework.HMW_STATES[1]:
                    #Name
                    if len(value) <= Homework.NAME_MAX_LENGTH:
                        self.name = value
                        res = res.substitute()

                        # Checking if subject has already been checked and testing the new tuple
                        if not self.inDB:
                            # Update HomeworkManager Observer to set subject suggestion
                            self._observer(self.id)
                        else:
                            self.updateState(False)
                            self._observer(self.id)
                            if not self.inDB:
                                res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state]
                                res = res.substitute(dateFormat = Homework.DATE_FORMAT['str'], dateExample = datetime.datetime.now().strftime(Homework.DATE_FORMAT['datetime']))
                                return (updateRes, res)
                            else:
                                return (updateRes, res)
                    else:
                        self.lastError = HomeworkMessage.HMW_CONF['longName'].substitute(maxCar = Homework.NAME_MAX_LENGTH)
                        self.lastChange = HomeworkMessage.HMW_CONF["wrongAction"].substitute(errorMsg = self.lastError)
                        self.updateState(True)
                        res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state].substitute()
                        return (False, res)
                elif self.state == Homework.HMW_STATES[2]:
                    #Subject
                    if value in self.subjectDBList:
                        # Subject input exist in DB
                        self.subject = value
                        res = res.substitute(dateFormat = Homework.DATE_FORMAT['str'], dateExample = datetime.datetime.now().strftime(Homework.DATE_FORMAT['datetime']))

                        # Reset this variable (even if not used)
                        self.subjectChoice = []

                        # Unicity check
                        self._observer(self.id)
                    else:
                        # Subjet input doesn't exist in DB
                        updateRes = False
                        self.subjectChoice = get_close_matches(value.lower(), self.subjectDBList, 2, Homework.WORD_SENSIBILITY)
                        if len(self.subjectChoice) > 0:
                            # Found at least one possibility possibility
                            if len(self.subjectChoice) > 1:
                                self.lastError = HomeworkMessage.HMW_CONF["subjectChoice"].substitute(sub = value, nbChoice = len(self.subjectChoice), plural1 = 's', plural2 = 'nt', subjectChoice = ', '.join(self.subjectChoice))
                            else:
                                self.lastError = HomeworkMessage.HMW_CONF["subjectChoice"].substitute(sub = value, nbChoice = len(self.subjectChoice), plural1 = '', plural2 = '', subjectChoice = ', '.join(self.subjectChoice))
                            res = HomeworkMessage.HMW_UTILS["subjectChoice"].substitute()
                        else:
                            # No matching subject for this input
                            self.lastError = HomeworkMessage.HMW_CONF["subjectError"].substitute(val = value, subjectList = ', '.join(self.subjectDBList))
                            self.subject = None
                            self.updateState(True)
                            res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state].substitute()
                        self.lastChange = HomeworkMessage.HMW_CONF["wrongAction"].substitute(errorMsg = self.lastError)
                        return (updateRes, res)
                elif self.state == Homework.HMW_STATES[3]:
                    #Date
                    (updateRes, res) = self.dateCheck(res, value)
                    if not updateRes:
                        return (updateRes, res)
                elif self.state == Homework.HMW_STATES[4]:
                    #Status
                    self.status = value
                    res = res.substitute(hmwRecap = self)

                    # Set the 'isComplete' boolean to inform that all required field are filled
                    # We can add documents if needed
                    self.isComplete = True
                else:
                    ## UNEXPECTED HOMEWORK.HMW_STATES ! HAVE TO BE CHECKED
                    pass
                self.lastChange = HomeworkMessage.HMW_CONF[self.state].substitute(var = value)

            elif self.userAction == Homework.HMW_USER_ACTION[1]:
                ##### HMW_EDIT
                pass

            elif self.userAction == Homework.HMW_USER_ACTION[2]:
                ##### HMW_DELETE
                if self.state == Homework.HMW_STATES[2]:
                    #Subject
                    if value in self.subjectDBList:
                        # Subject input exist in DB
                        self.subject = value

                        # Reset this variable (even if not used)
                        self.subjectChoice = []

                        res = res.substitute(hmwList = '')
                    else:
                        # Subjet input doesn't exist in DB
                        updateRes = False
                        self.subjectChoice = get_close_matches(value.lower(), self.subjectDBList, 2, Homework.WORD_SENSIBILITY)
                        if len(self.subjectChoice) > 0:
                            # Found at least one possibility possibility
                            if len(self.subjectChoice) > 1:
                                self.lastError = HomeworkMessage.HMW_CONF["subjectChoice"].substitute(sub = value, nbChoice = len(self.subjectChoice), plural1 = 's', plural2 = 'nt', subjectChoice = ', '.join(self.subjectChoice))
                            else:
                                self.lastError = HomeworkMessage.HMW_CONF["subjectChoice"].substitute(sub = value, nbChoice = len(self.subjectChoice), plural1 = '', plural2 = '', subjectChoice = ', '.join(self.subjectChoice))
                            res = HomeworkMessage.HMW_UTILS["subjectChoice"].substitute()
                        else:
                            # No matching subject for this input
                            self.lastError = HomeworkMessage.HMW_CONF["subjectError"].substitute(val = value, subjectList = ', '.join(self.subjectDBList))
                            self.subject = None
                            self.updateState(True)
                            res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state].substitute()
                        self.lastChange = HomeworkMessage.HMW_CONF["wrongAction"].substitute(errorMsg = self.lastError)
                        return (updateRes, res)
            else:
                # MUST BE AN ERROR --> Check it here
                pass
        return (updateRes, res)
    
    def updateDocStatus(self, status):
        res = None
        docStateIdx = Homework.HMW_STATES_SEQ[self.userAction].index(Homework.HMW_STATES[5])
        if self.state == Homework.HMW_STATES_SEQ[self.userAction][docStateIdx - 1]:
            self.docAwaited = status
            self.updateState(False)
            self.lastChange = HomeworkMessage.HMW_CONF['docUpdated'].substitute()
            res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state].substitute(hmwRecap = self)
        return res

    def updateDoc(self, docs):
        if self.state == Homework.HMW_STATES_SEQ[self.userAction][-1] and self.docAwaited:
            docMsg = ''
            for doc in docs:
                self.doc = doc
                docMsg += HomeworkMessage.HMW_CONF["docAdded"].substitute(docName = doc.filename)
            self.lastChange = docMsg
            res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state].substitute(hmwRecap = self)
            return res
        return None

    def numberedAddAction(self, voteIdx):
        res = ""
        if self.state == Homework.HMW_STATES[1]:
            # If still in 'name' state --> user choose the suggested subject in reaction
            self.subject = self.suggSubject
            self.updateState(False)

            # Homework now in Homework.HMW_STATES[2] ('subject')
            res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state]
            res = res.substitute(dateFormat = Homework.DATE_FORMAT['str'], dateExample = datetime.datetime.now().strftime(Homework.DATE_FORMAT['datetime']))
            self.lastChange = HomeworkMessage.HMW_CONF[self.state].substitute(var = self.suggSubject)

            # Reset this variable (even if not used)
            self.subjectChoice = []

            # Activate the HomeworkManager observer to check the unicity of the new homework
            self._observer(self.id)
        else:
            # Already in 'Subject' state --> user is choosing between the possible subject from its input
            if voteIdx < len(self.subjectChoice):
                if self.state == Homework.HMW_STATES[2]:
                    self.subject = self.subjectChoice[voteIdx]
                    res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state].substitute(dateFormat = Homework.DATE_FORMAT['str'], dateExample = datetime.datetime.now().strftime(Homework.DATE_FORMAT['datetime']))
                    self.lastChange = HomeworkMessage.HMW_CONF[self.state].substitute(var = self.subjectChoice[voteIdx])
                    # print(f"HOMEWORK - Last change: {self.lastChange}")

                    # Reset this variable (even if not used)
                    self.subjectChoice = []

                    # Activate the HomeworkManager observer to check the unicity of the new homework
                    self._observer(self.id)
            else:
                pass
        return res

    def numberedEditAction(self, number):
        pass

    def numberedDeleteAction(self, number):
        res = ""
        if self.state == Homework.HMW_STATES[0]:
            # If still in 'idle' state --> user choose the suggested subject in reaction
            self.subject = self.suggSubject
            self.updateState(False)

            # Homework now in Homework.HMW_STATES[2] ('subject')
            res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state]
            res = res.substitute(hmwList = '')
            self.lastChange = HomeworkMessage.HMW_CONF[self.state].substitute(var = self.suggSubject)
        elif self.state == Homework.HMW_STATES[2]:
            # Already in 'Subject' state --> user is choosing between the possible subject from its input
            if len(self.subjectChoice) > 0:
                # User selecting a subject in reaction after trying to enter one by message
                if (self.state == Homework.HMW_STATES[2] and number < len(self.subjectChoice)):
                    # Subject
                    self.subject = self.subjectChoice[number]
                    res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state].substitute(hmwList = '')
                    self.lastChange = HomeworkMessage.HMW_CONF[self.state].substitute(var = self.subjectChoice[number])

                    # Reset this variable (even if not used)
                    self.subjectChoice = []
            else:
                # User selecting an homework from the displayed numbered list
                number = number + 1 # Resetting the official value from the parameter (reduced in HomeworkManager)
                self._observer(self.id, number) # Sets the selected homework in the self.selectedSubject

                self.updateState(False)

                self.lastChange = HomeworkMessage.HMW_CONF['homeworkChosen'].substitute(nomDevoir = self.selectedSubject['name'])
                hmwDesc = HomeworkMessage.HMW_DESC['global'].substitute(subject = self.selectedSubject['subject'], nom = self.selectedSubject['name'], status = 'None', date = self.selectedSubject['deadline'].strftime(Homework.DATE_FORMAT['datetime']))
                res = Homework.HMW_ACTION_MSG_DIC[self.userAction][self.state].substitute(hmwToDelete = hmwDesc)
                self.isComplete = True
        else:
            #Other state ?
            pass
        return res