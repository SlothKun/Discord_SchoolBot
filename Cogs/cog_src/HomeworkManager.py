from .Homework import Homework

class HomeworkManager():

    HMW_ACTIONS = ["hmwAdd", "hmwEdit", "hmwDelete"]

    def __init__(self):
        self._homeworks = {}
        self._linkedBotMsg = {}
    
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
    def linkedBotMsg(self):
        return self._linkedBotMsg

    def hmwObserver(self, creatorID, hmwComplete):
        hmw = self.homeworks[creatorID]
        res = ""
        if hmw.userAction == HomeworkManager.HMW_ACTIONS[0]:
            ## Adding an homework
            res = "\n**Ajout d'un nouveau devoir - Récapitulatif :**"
            res += f"\n{hmw}"
            if not hmwComplete:
                # All data are filled but the related document expected
                res += "\nVous avez spécifié qu'un document devait être lié au devoir, mais aucun document n'a été reçu."
                res += "\nVeuillez glisser un document dans ce salon ou ignorez ce message pour valider l'ajout du document"
            res += "\n\nVeuillez utiliser les réactions ci-dessous pour confirmer l'ajout de ce devoir"
        elif hmw.userAction == HomeworkManager.HMW_ACTIONS[1]:
            ## Editing an homework
            pass
        elif hmw.userAction == HomeworkManager.HMW_ACTIONS[2]:
            ## Deleting an homework
            pass

    def checkHmw(self, creatorID):
        return creatorID in self.homeworks

    def newHmw(self, creatorID, hmwAction, botMsgId):
        print(f"HMW_MAN - Creating a new homework for {creatorID} in mode {HomeworkManager.HMW_ACTIONS[hmwAction]}")
        self.homeworks[creatorID] = Homework(creatorID, HomeworkManager.HMW_ACTIONS[hmwAction], self.hmwObserver)
        self.linkedBotMsg[creatorID] = botMsgId

    def checkHmwState(self, creatorID):
        if self.homeworks[creatorID].state == HomeworkManager.substates[self.homeworks[creatorID].userAction][-1] and self.homeworks[creatorID].isComplete():
            return True
        return False

    def updateBotMsg(self, creatorID, newBotMsgID):
        self.linkedBotMsg[creatorID] = newBotMsgID

    def updateActionState(self, newState):
        self.actionSubState = self.subStates[self.userAction][self.subStateCounter]

    def getNbSubState(self, creatorID):
        return self.homeworks[creatorID].nbStep

    def updateHmw(self, creatorID, value, isBack = False):
        self.homeworks[creatorID].updateVal(value, isBack)

    def checkNextAction(self, creatorID, nextCommand):
        # Check if user is allowed to performed next command
        # Depends on the state and substates of the homework
        if self.homeworks[creatorID].userAction == HomeworkManager.states[0]:
            # State == hmw add
            if nextCommand == 'Name':
                return self.actionSubState is None
            elif nextCommand == 'Date':
                return self.actionSubState == self.subStates[self.userAction][0]
            elif nextCommand == 'Status':
                return self.actionSubState == self.subStates[self.userAction][1]
            elif nextCommand == 'Subject':
                return self.actionSubState == self.subStates[self.userAction][2]
        elif self.homeworks[creatorID].userAction == HomeworkManager.states[1]:
            # State == hmw edition
            if nextCommand == 'Name':
                return self.actionSubState is None
            elif nextCommand == 'PartToEdit':
                return self.actionSubState == self.subStates[self.userAction][0]
        elif self.homeworks[creatorID].userAction == HomeworkManager.states[2]:
            # state == hmw deletion
            if nextCommand == 'Name':
                return self.actionSubState is None
        return False