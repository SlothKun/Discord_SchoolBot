import datetime
from string import Template

class HomeworkMessage():
    HMW_UTILS = {
        "formatingQuote": "```",
        "separationLine" : "\n\n-----------------\nCliquez sur les réactions en-dessous du message pour interagir des façons suivantes:",

        "cancel": Template("\n\t$emoji - Annuler $userAction du devoir"),
        "back": Template("\n\t$emoji - Annuler dernière action"),
        "addFile": Template("\n\t$emoji - Ajouter un document au devoir"),
        "modifConf": Template("\n\t$emoji - Confirmer $userAction du devoir")
    }

    HMW_ADD = {
        "title": Template("**Ajout d'un nouveau devoir - Étape $stepNum/$totalStep**\n"),

        "idle": Template("Veuillez préciser le nom du devoir que vous souhaitez créer \n\t - ex: 'Devoir maison #1'"),
        "name": Template("Veuillez préciser la date limite du devoir que vous souhaitez créer \n\tLe format de la date doit être le suivant '$dateFormat' - ex: $dateExample"),
        "date": Template("Veuillez préciser le statut du devoir que vous souhaitez créer \n\t - ex: 'À rendre', 'Obligatoire'"),
        "status": Template("Veuillez préciser la matière du devoir que vous souhaitez créer \n\t - ex: 'Mathématiques', 'Physique'"),
        "subject": Template("$hmwRecap")
    }

    HMW_EDIT = {}

    HMW_DELETE = {}

    HMW_CONF = {
        "name": Template("Nom *'$var'* a bien été enregistré"),
        "date": Template("Date *'$var'* a bien été enregistrée"),
        "status": Template("Status *'$var'* a bien été enregistré"),
        "subject": Template("Matière *'$var'* a bien été enregistrée"),
        "docUpdated": Template("Un fichier devra être lié au devoir en cours de création.\nle prochain fichier que vous enverrez dans ce salon sera lié à ce devoir"),

        "cancelledAction": Template("Dernière action '$oldVal' annulée"),
        "wrongAction": Template("Dernière action n'a pas pu être enregistrée : \n\t$errorMsg"),

        "backMessage": Template("Dernière modification ($lastModif) a bien été annulée"),
        "cancelMessage": Template("$userAction du devoir a bien été annulé"),

        "dbUpdated": Template("Devoir enregistré dans la base de données")
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

class Homework():

    HMW_STATES = {
        "hmwAdd" : ["idle", "name", "date", "status", "subject"],
        "hmwEdit" : ["idle", "name", "partToEdit", ""],
        "hmwDelete" : ["idle", "name"]
    }

    HMW_USER_ACTION = {
        "hmwAdd": "ajout",
        "hmwEdit": "édition",
        "hmwDelete": "suppression"
    }

    def __init__(self, creator, userAction, observerFunc):
        self._creator = creator
        self._creationDate = datetime.datetime.utcnow()
        self._observer = observerFunc

        self._userAction = userAction
        self._state = Homework.HMW_STATES[self.userAction][0]
        self._lastChange = ""
        self._lastError = ""
        self._isComplete = False

        self._name = ""
        self._docAwaited = False
        self._doc = []
        self._deadline = None
        self._status = None
        self._subject = None

    def __str__(self):
        desc = f"Devoir de {self.subject} : {self.name}\nStatut : {self.status}\nPour le {self.date.strftime('%d %B %Y')}"
        if len(self.doc) > 0:
            desc += f"{len(self.doc)} document(s) associé(s):"
            for doc in self.doc:
                desc += f"\t*{doc.filename}*"
        else:
            desc += "\nAucun document associé"
        return desc

    def hmwDict(self):
        hmwDict = {}
        hmwDict['name'] = self.name
        hmwDict['publish_date'] = self._creationDate
        hmwDict['deadline'] = self.date
        hmwDict['creator'] = {'name': self.id}
        hmwDict['subject'] = self.subject
        hmwDict['cible'] = 'TS1'
        return hmwDict

    ## GETTERs
    @property
    def id(self):
        return self._creator
    
    @property
    def age(self):
        return (datetime.datetime.utcnow() - self._creationDate).total_seconds()

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
        self.lastChange = f"Ajout de fichier pour ce devoir autorisé\n"
    
    @doc.setter
    def doc(self, value):
        self._doc.append(value)
        self.lastChange = f"Fichier {value.filename} a bien été ajouté\n"
    
    @date.setter
    def date(self, value):
        self._deadline = value
        # if value is not None:
        #     self.lastChange = f"Date {value.strftime('%Y-%m-%d')} a bien été enregistrée\n"
    
    @status.setter
    def status(self, value):
        self._status = value
        # self.lastChange = f"Statut {value} a bien été enregistré\n"
    
    @subject.setter
    def subject(self, value):
        self._subject = value
        # self.lastChange = f"Matière {value} a bien été enregistrée\n"

    ## UTILITY FUNCTIONs
    def isDocNeeded(self):
        # Function to check if the document required by the creator has been sent
        if self.docAwaited and len(self.doc) == 0:
            return False
        return True

    def updateState(self, isBack):
        # Function to update the state of the current homework forward or backward if needed
        if isBack:
            # del self.lastChange.split('\n')[-1]
            self.state = Homework.HMW_STATES[self.userAction][max(0, Homework.HMW_STATES[self.userAction].index(self.state) - 1)]
        else:
            self.state = Homework.HMW_STATES[self.userAction][min(len(Homework.HMW_STATES[self.userAction]), Homework.HMW_STATES[self.userAction].index(self.state) + 1)]
    
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
                res = res.substitute(dateFormat = 'AAAA-MM-JJ', dateExample = datetime.datetime.now().strftime('%Y-%m-%d'))
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
                res = res.substitute(dateFormat = 'AAAA-MM-JJ', dateExample = datetime.datetime.now().strftime('%Y-%m-%d'))
            elif self.state == Homework.HMW_STATES[self.userAction][2]:
                #Date
                try:
                    self.date = datetime.datetime.strptime(value, "%Y-%m-%d")
                    res = res.substitute()
                except ValueError as ve:
                    self.lastError = f"Erreur de format de date:\n\tLe format de la date doit être le suivant 'AAAA-MM-JJ' - ex: {datetime.datetime.now().strftime('%Y-%m-%d')}"
                    self.lastChange = HomeworkMessage.HMW_CONF["wrongAction"].substitute(errorMsg = self.lastError)
                    self.date = None
                    self.updateState(True)
                    res = HomeworkMessage.HMW_ADD[self.state].substitute(dateFormat = 'AAAA-MM-JJ', dateExample = datetime.datetime.now().strftime('%Y-%m-%d'))
                    return (False, res)
            elif self.state == Homework.HMW_STATES[self.userAction][3]:
                #Status
                self.status = value
                res = res.substitute()
            elif self.state == Homework.HMW_STATES[self.userAction][4]:
                #Subject
                self.subject = value
                res = res.substitute(hmwRecap = self)
                self.isComplete = True
                self._observer(self.id, self.isDocNeeded())
            self.lastChange = HomeworkMessage.HMW_CONF[self.state].substitute(var = value)
        return (True, res)
    
    def updateDocStatus(self, status):
        self.docAwaited = status
        res = HomeworkMessage.HMW_ADD[self.state]
        if self.state == Homework.HMW_STATES[self.userAction][1]:
            res = res.substitute(dateFormat = 'AAAA-MM-JJ', dateExample = datetime.datetime.now().strftime('%Y-%m-%d'))
        else:
            res = res.substitute()
        return res