from .HomeworkMessage import HomeworkMessage

import datetime

from string import Template
from difflib import get_close_matches

class Homework():

    HMW_STATES = {
        "hmwAdd" : ["idle", "name", "date", "status", "subject", "document"],
        "hmwEdit" : ["idle", "name", "partToEdit", ""],
        "hmwDelete" : ["idle", "name"]
    }

    HMW_USER_ACTION = {
        "hmwAdd": "ajout",
        "hmwEdit": "édition",
        "hmwDelete": "suppression"
    }

    DATE_FORMAT = {
        'datetime': '%d/%m',
        'str': 'JJ/MM',
        'strptime': '%Y/%d/%m'
    }

    WORD_SENSIBILITY = 0.4

    def __init__(self, creator, userAction, observerFunc, subjectList, suggSubject):
        self._creator = creator
        self._creationDate = datetime.datetime.utcnow()
        self._suggestedSubject = suggSubject
        self._observer = observerFunc

        self._userAction = userAction
        self._state = Homework.HMW_STATES[self.userAction][0]
        self._lastChange = ""
        self._lastError = ""
        self._isComplete = False

        self._name = ""
        self._docAwaited = False
        self._doc = []
        self._dedicatedChanID = None
        self._deadline = None
        self._status = None
        self._subject = None

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
    def userAction(self):
        return self._userAction

    @property
    def userActionName(self):
        return Homework.HMW_USER_ACTION[self.userAction]

    @property
    def state(self):
        return self._state

    @property
    def stateIdx(self):
        return Homework.HMW_STATES[self.userAction].index(self.state)

    @property
    def lastError(self):
        return self._lastError

    @property
    def lastChange(self):
        temp = self._lastChange
        self._lastChange = ""
        return temp

    @property
    def isComplete(self):
        return self._isComplete

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
            return len(Homework.HMW_STATES[self.userAction]) - 1
        return len(Homework.HMW_STATES[self.userAction])

    ##########
    ########## 
    ## SETTERs
    ##########
    ##########

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
        self._lastChange += value

    @isComplete.setter
    def isComplete(self, value):
        self._isComplete = value

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

    def updateState(self, isBack):
        # Function to update the state of the current homework forward or backward if needed
        if isBack:
            # del self.lastChange.split('\n')[-1]
            self.state = Homework.HMW_STATES[self.userAction][max(0, self.stateIdx - 1)]
        else:
            self.state = Homework.HMW_STATES[self.userAction][min((len(Homework.HMW_STATES[self.userAction]) - 1), self.stateIdx + 1)]
    
    def updateVal(self, value, isBack):
        res = None
        emojis = []
        if isBack:
            # Canceling last modification
            self.updateState(isBack)
            res = HomeworkMessage.HMW_ADD[self.state]
            oldValue = ""
            if self.state == Homework.HMW_STATES[self.userAction][0]:
                #Idle
                oldValue = self.name
                self.name = None
                res = res.substitute()
            elif self.state == Homework.HMW_STATES[self.userAction][1]:
                #Name
                oldValue = self.date
                self.date = None
                res = res.substitute(dateFormat = Homework.DATE_FORMAT['str'], dateExample = datetime.datetime.now().strftime(Homework.DATE_FORMAT['datetime']))
            elif self.state == Homework.HMW_STATES[self.userAction][2]:
                #Date
                oldValue = self.status
                self.status = None
                res = res.substitute()
            elif self.state == Homework.HMW_STATES[self.userAction][3]:
                #Status
                oldValue = self.subject
                self.subject = None
                res = res.substitute()
            elif self.state == Homework.HMW_STATES[self.userAction][4]:
                #subject
                oldValue = self.subject
                res = res.substitute()
            self.lastChange =  HomeworkMessage.HMW_CONF["cancelledAction"].substitute(oldVal = oldValue)
        else:
            self.updateState(isBack)
            res = HomeworkMessage.HMW_ADD[self.state]
            # Adding a new property
            if self.state == Homework.HMW_STATES[self.userAction][1]:
                #Name
                self.name = value
                res = res.substitute(dateFormat = Homework.DATE_FORMAT['str'], dateExample = datetime.datetime.now().strftime(Homework.DATE_FORMAT['datetime']))
            elif self.state == Homework.HMW_STATES[self.userAction][2]:
                #Date
                try:
                    value = str(datetime.datetime.now().year) + '/' + value
                    self.date = datetime.datetime.strptime(value, Homework.DATE_FORMAT['strptime'])
                    #TODO: Vérifier que la date est bien supérieure à la date d'aujourd'hui
                    res = res.substitute()
                except ValueError as ve:
                    self.lastError = HomeworkMessage.HMW_CONF['dateError'].substitute(dateFormat = Homework.DATE_FORMAT['str'], date = datetime.datetime.now().strftime(Homework.DATE_FORMAT['datetime']))
                    self.lastChange = HomeworkMessage.HMW_CONF["wrongAction"].substitute(errorMsg = self.lastError)
                    self.date = None
                    self.updateState(True)
                    res = HomeworkMessage.HMW_ADD[self.state].substitute(dateFormat = Homework.DATE_FORMAT['str'], dateExample = datetime.datetime.now().strftime(Homework.DATE_FORMAT['datetime']))
                    return (False, res)
            elif self.state == Homework.HMW_STATES[self.userAction][3]:
                #Status
                self.status = value
                res = res.substitute()
                self._observer(self.id)
            elif self.state == Homework.HMW_STATES[self.userAction][4]:
                #Subject
                if value in self.subjectDBList:
                    # Subject input exist in DB
                    self.subject = value
                    res = res.substitute(hmwRecap = self)
                    self.isComplete = True
                else:
                    # Subjet input doesn't exist in DB
                    self.subjectChoice = get_close_matches(value.lower(), self.subjectDBList, 2, Homework.WORD_SENSIBILITY)
                    if len(self.subjectChoice) > 0:
                        # Found at least one possibility possibility
                        if len(self.subjectChoice) > 1:
                            self.lastError = HomeworkMessage.HMW_CONF["subjectChoice"].substitute(sub = value, nbChoice = len(self.subjectChoice), plural1 = 's', plural2 = 'nt', subjectChoice = ', '.join(self.subjectChoice))
                        else:
                            self.lastError = HomeworkMessage.HMW_CONF["subjectChoice"].substitute(sub = value, nbChoice = len(self.subjectChoice), plural1 = '', plural2 = '', subjectChoice = ', '.join(self.subjectChoice))
                        self.lastChange = HomeworkMessage.HMW_CONF["wrongAction"].substitute(errorMsg = self.lastError)
                        res = HomeworkMessage.HMW_ADD["subjectChoice"].substitute()
                    else:
                        # No matching subject for this input
                        self.lastError = HomeworkMessage.HMW_CONF["subjectError"].substitute(val = value, subjectList = ', '.join(self.subjectDBList))
                        self.lastChange = HomeworkMessage.HMW_CONF["wrongAction"].substitute(errorMsg = self.lastError)
                        self.subject = None
                        self.updateState(True)
                        res = HomeworkMessage.HMW_ADD[self.state].substitute()
                    return (False, res)
            self.lastChange = HomeworkMessage.HMW_CONF[self.state].substitute(var = value)
        return (True, res)
    
    def updateDocStatus(self, status):
        res = None
        if self.state == Homework.HMW_STATES[self.userAction][4]:
            self.docAwaited = status
            self.updateState(False)
            self.lastChange = HomeworkMessage.HMW_CONF['docUpdated'].substitute()
            res = HomeworkMessage.HMW_ADD[self.state].substitute(hmwRecap = self)
        return res

    def updateDoc(self, docs):
        print(f"HOMEWORK - File to set for {len(docs)} docs")
        if self.state == Homework.HMW_STATES[self.userAction][-1]:
            self.lastChange = ""
            for doc in docs:
                self.doc = doc
                self.lastChange += HomeworkMessage.HMW_CONF["docAdded"].substitute(docName = doc.filename)
            res = HomeworkMessage.HMW_ADD[self.state].substitute(hmwRecap = self)
            return res
        return None

    def setNewSubjectVal(self, voteIdx):
        res = ""
        if self.state == Homework.HMW_STATES[self.userAction][3]:
            # If still in 'Status' state --> user choose the subject in reaction
            self.subject = self.suggSubject
            self.updateState(False)
            res = HomeworkMessage.HMW_ADD[self.state]
            res = res.substitute(hmwRecap = self)
            self.isComplete = True
            self.lastChange = HomeworkMessage.HMW_CONF[self.state].substitute(var = self.suggSubject)
        else:
            # Already in 'Subject' state --> user is choosing between the possible subject from its input
            if voteIdx < len(self.subjectChoice):
                if self.state == Homework.HMW_STATES[self.userAction][4]:
                    self.subject = self.subjectChoice[voteIdx]
                    res = HomeworkMessage.HMW_ADD[self.state].substitute(hmwRecap = self)
                    self.isComplete = True
                    self.lastChange = HomeworkMessage.HMW_CONF[self.state].substitute(var = self.subjectChoice[voteIdx])
            else:
                pass
        return res