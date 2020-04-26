import datetime
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
        "title": Template("**- Ajout d'un nouveau devoir - Étape $stepNum/$totalStep**\n"),

        "idle": Template("Veuillez préciser le nom du devoir que vous souhaitez créer \n\t - ex: 'Devoir maison #1'"),
        "name": Template("Veuillez préciser la date limite du devoir que vous souhaitez créer \n\tLe format de la date doit être le suivant '$dateFormat' - ex: $dateExample"),
        "date": Template("Veuillez préciser le statut du devoir que vous souhaitez créer \n\t - ex: 'À rendre', 'Obligatoire'"),
        "status": Template("Veuillez préciser la matière du devoir que vous souhaitez créer \n\t - ex: 'Mathématiques', 'Physique'"),
        "subject": Template("$hmwRecap")
    }

    HMW_EDIT = {}

    HMW_DELETE = {}

    HMW_CONF = {
        "name": Template("Nom $nameVar a bien été enregistré"),
        "date": Template("Date $dateVar a bien été enregistrée"),
        "status": Template("Status $statusVar a bien été enregistré"),
        "subject": Template("Matière $subjectVar a bien été enregistrée"),

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

    HMW_EMOJIS = ["cancel", "back", "addFile", "modifConf"]

    def __init__(self, creator, userAction, observerFunc):
        self._creator = creator
        self._creationDate = datetime.datetime.utcnow()
        self._observer = observerFunc

        self._userAction = userAction
        self._state = Homework.HMW_STATES[self.userAction][0]
        self._lastChange = ""
        self._lastError = ""

        self._name = ""
        self._docAwaited = False
        self._doc = []
        self._deadline = None
        self._status = None
        self._subject = None

        self.hmwEmojis = [Homework.HMW_EMOJIS[0]]

    def __str__(self):
        desc = f"Devoir de {self.subject} : {self.name}\nStatut : {self.status}\nPour le {self.date.strftime('%d %B %Y')}"
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

    @name.setter
    def name(self, value):
        self._name = value
        self.lastChange = f"Nom {value} a bien été enregistré\n"
    
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
        if value is not None:
            self.lastChange = f"Date {value.strftime('%Y-%m-%d')} a bien été enregistrée\n"
    
    @status.setter
    def status(self, value):
        self._status = value
        self.lastChange = f"Statut {value} a bien été enregistré\n"
    
    @subject.setter
    def subject(self, value):
        self._subject = value
        self.lastChange = f"Matière {value} a bien été enregistrée\n"

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
        if isBack:
            # Canceling last modification
            if self.state == Homework.HMW_STATES[self.userAction][1]:
                #Name
                self.name = None
            elif self.state == Homework.HMW_STATES[self.userAction][2]:
                #Date
                self.date = None
            elif self.state == Homework.HMW_STATES[self.userAction][3]:
                #Status
                self.status = None
            elif self.state == Homework.HMW_STATES[self.userAction][4]:
                #Subject
                self.subject = None
            self.updateState(isBack)
        else:
            self.updateState(isBack)
            # Adding a new property
            if self.state == Homework.HMW_STATES[self.userAction][1]:
                #Name
                self.name = value
            elif self.state == Homework.HMW_STATES[self.userAction][2]:
                #Date
                try:
                    self.date = datetime.datetime.strptime(value, "%Y-%m-%d")
                except ValueError as ve:
                    self.lastError = f"Erreur de format de date:\n\tLe format de la date doit être le suivant 'AAAA-MM-JJ' - ex: {datetime.datetime.now().strftime('%Y-%m-%d')}"
                    self.updateVal(None, True)
                    return False
            elif self.state == Homework.HMW_STATES[self.userAction][3]:
                #Status
                self.status = value
            elif self.state == Homework.HMW_STATES[self.userAction][4]:
                #Subject
                self.subject = value
                self._observer(self.id, self.isDocNeeded())
        return True