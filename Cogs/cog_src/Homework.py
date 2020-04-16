import datetime

class Homework():

    HMW_STATES = {
        "hmwAdd" : ["idle", "name", "date", "status", "subject"],
        "hmwEdit" : ["idle", "name", "partToEdit", ""],
        "hmwDelete" : ["idle", "name"]
    }

    def __init__(self, creator, userAction, observerFunc):
        self._creator = creator
        self._creationDate = datetime.datetime.now()
        self._observer = observerFunc

        self._userAction = userAction
        self._state = Homework.HMW_STATES[self.userAction][0]

        self._name = ""
        self._docAwaited = False
        self._doc = []
        self._deadline = None
        self._status = None
        self._subject = None

    def __str__(self):
        desc = f"Devoir de {self.subject} : {self.name}\nStatut : {self.status}\nPour le {self.deadline.strftime('%d %B %Y')}"
        if len(self.doc) > 0:
            desc += f"{len(self.doc)} document(s) associé(s):"
            for doc in self.doc:
                desc += f"\t*{doc.filename}*"
        else:
            desc += "\nAucun document associé"
        return desc

    ## GETTERs
    @property
    def id(self):
        return self._creator

    @property
    def userAction(self):
        return self._userAction

    @property
    def state(self):
        return self._state

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
        return len(Homework.HMW_STATES[self.userAction])
       
    ## SETTERs
    @userAction.setter
    def userAction(self, value):
        self._userAction = value
        
    @state.setter
    def state(self, value):
        self._state = value
        if self._state == Homework.HMW_STATES[self._userAction][-1]:
            self._observer(self.id, self.isDocNeeded())

    @name.setter
    def name(self, value):
        self._name = value
    
    @docAwaited.setter
    def docAwaited(self, value):
        self._docAwaited = value
    
    @doc.setter
    def doc(self, value):
        self._doc.append(value)
    
    @date.setter
    def date(self, value):
        self._deadline = value
    
    @status.setter
    def status(self, value):
        self._status = value
    
    @subject.setter
    def subject(self, value):
        self._subject = value

    ## UTILITY FUNCTIONs
    def isDocNeeded(self):
        # Function to check if the document required by the creator has been sent
        if self.docAwaited and len(self.doc) == 0:
            return False
        return True

    def updateState(self, isBack):
        # Function to update the state of the current homework forward or backward if needed
        if isBack:
            self.state = Homework.HMW_STATES[self.userAction][max(0, Homework.HMW_STATES[self.userAction].index(self.state) - 1)]
        else:
            self.state = Homework.HMW_STATES[self.userAction][min(len(Homework.HMW_STATES[self.userAction]), Homework.HMW_STATES[self.userAction].index(self.state) + 1)]
    
    def updateVal(self, value, isBack):
        self.updateState(isBack)
        if isBack:
            # Adding a new property
            pass
        else:
            # Canceling last modification
            pass