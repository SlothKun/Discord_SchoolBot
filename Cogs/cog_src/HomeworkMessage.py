from string import Template

class HomeworkMessage():
    HMW_UTILS = {
        "formatingQuote": "```",
        "formatingQuoteDiff": "```diff\n",
        "separationLine" : "\n\n-----------------\nCliquez sur les réactions en-dessous du message pour interagir des façons suivantes:",

        "cancel": Template("\n\t$emoji - Annuler $userAction du devoir"),
        "back": Template("\n\t$emoji - Annuler dernière action"),
        "addFile": Template("\n\t$emoji - Ajouter un document au devoir"),
        "modifConf": Template("\n\t$emoji - Confirmer $userAction du devoir")
    }

    HMW_ADD = {
        "title": Template("**Ajout d'un nouveau devoir - Étape $stepNum/$totalStep**\n"),

        "idle": Template("Veuillez préciser le nom du devoir que vous souhaitez créer \n\t - ex: 'Devoir maison #1'"),
        "name": Template("Veuillez préciser la matière du devoir que vous souhaitez créer \n\t - ex: 'Mathématiques', 'Physique'"),
        "date": Template("Veuillez préciser le statut du devoir que vous souhaitez créer \n\t - ex: 'À rendre', 'Optionel'"),
        "status": Template("$hmwRecap"),
        "subject": Template("Veuillez préciser la date limite du devoir que vous souhaitez créer \n\tLe format de la date doit être le suivant '$dateFormat' - ex: $dateExample"),
        "document": Template("$hmwRecap"),

        "subjectSuggested": Template("\nLa matière '$subject' vous est suggérée, vous pouvez la sélectionner en cliquant sur la réaction $reac"),
        "subjectChoice": Template("Veuillez sélectioner les réactions ci-dessous pour affiner votre choix:"),
        "subjectChoiceReac": Template("\n\tUtilisez la réaction $reac pour sélectionner la matiere '$subject'"),
    }

    HMW_EDIT = {}

    HMW_DELETE = {}

    HMW_CONF = {
        "name": Template("+ Nom '$var' a bien été enregistré +"),
        "date": Template("+ Date '$var' a bien été enregistrée +"),
        "status": Template("+ Statut '$var' a bien été enregistré +"),
        "subject": Template("+ Matière '$var' a bien été enregistrée +"),
        "docUpdated": Template("+ Autorisation d'associer un fichier à ce devoir.\nLes prochains fichiers que vous enverrez dans ce salon seront liés à ce devoir +"),
        "docAdded": Template("+ Document $docName a bien été ajouté +\n"),

        "cancelledAction": Template("+ Dernière action '$oldVal' annulée +"),
        "wrongAction": Template("- Dernière action n'a pas pu être enregistrée : -\n-\t$errorMsg"),
        "dateError": Template("Erreur de format de date:\n\tLe format de la date doit être le suivant '$dateFormat' - ex: $date"),
        "dateInf": Template("Date antérieure:\n\tLa date entrée est trop ancienne"),
        "longName": Template("Le nom entré ne doit pas excéder $maxCar caractères\n\tVeuillez entrer un nom plus court"),

        
        'subjectError': Template("- Aucune matière renseignée ne correspond à l'entrée '$val'. Liste des matières renseignées: -\n$subjectList"),
        'subjectChoice': Template("- Matière '$sub' non renseignée, mais $nbChoice possibilité$plural1 existe$plural2: $subjectChoice  -"),

        "backMessage": Template("+ Dernière modification ($lastModif) a bien été annulée +"),
        "cancelMessage": Template("+ $userAction du devoir a bien été annulé +"),

        "dbUpdated": Template("+ Devoir enregistré dans la base de données +"),

        "hmwDeleted": Template("+ Devoir en cours de création a été supprimé +")
    }

    HMW_DESC = {
        "global": Template("Devoir de $subject : $nom\nStatut : $status\nPour le $date"),
        "docList": Template("\n$nbDoc document$plural associé$plural:"),
        "docName": Template("\n\t- $docName"),
        "docSuggestion": Template("\nAucun document associé\n\tSi vous souhaitez lier un document à ce devoir, utiliser la réaction correspondante ci-dessous")
    }

    @classmethod
    def stateDisplayer(cls, stateNum):
        stateFR = ['Nom', 'Matiere', 'Date', 'Statut', 'Document']
        # if stateNum > 0:
        if stateNum == 0:
            res = '[' + stateFR[0] + '] -> '
            res += ' -> '.join(stateFR[1:])
            return res
        elif stateNum == len(stateFR):
            res = '~~'
            res += '~~ -> ~~'.join(stateFR[0:-1])
            res += '~~ -> [' + stateFR[-1] + ']'
            return res
        res = '~~'
        res += '~~ -> ~~'.join(stateFR[0:(stateNum)])
        res += '~~ -> [' + stateFR[(stateNum)] + ']'
        if (stateNum + 1) < len(stateFR):
            res += ' -> ' + ' -> '.join(stateFR[(stateNum + 1):])
        return res
    
    @classmethod
    def diffFormatMsg(cls, msg):
        res = HomeworkMessage.HMW_UTILS['formatingQuoteDiff'] + msg + HomeworkMessage.HMW_UTILS['formatingQuote']
        return str(res)