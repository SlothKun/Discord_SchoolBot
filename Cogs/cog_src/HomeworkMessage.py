from string import Template

class HomeworkMessage():
    HMW_UTILS = {
        "formatingQuote": "```",
        "formatingQuoteDiff": "```diff\n",
        "separationLine" : "\n\n-----------------\nCliquez sur les réactions en-dessous du message pour interagir des façons suivantes:",

        "cancel": Template("\n\t$emoji - Annuler $userAction du devoir"),
        "back": Template("\n\t$emoji - Annuler dernière action"),
        "addFile": Template("\n\t$emoji - Ajouter un document au devoir"),
        "modifConf": Template("\n\t$emoji - Confirmer $userAction du devoir"),
        "nextElemsInDB": Template("\n\t$emoji - Afficher plus de devoirs"),

        "subjectSuggested": Template("\nLa matière '$subject' vous est suggérée, vous pouvez la sélectionner en cliquant sur la réaction $reac"),
        "subjectChoice": Template("Veuillez sélectioner les réactions ci-dessous pour affiner votre choix:"),
        "subjectChoiceReac": Template("\n\tUtilisez la réaction $reac pour sélectionner la matiere '$subject'"),

        "inDB": Template("Veuillez entrer un nouveau nom pour ce devoir afin d'éviter les conflits.\n\tAncien nom : $oldName"),
        "hmwdisp": Template("\n\t\t* $emoji : $hmwname")
    }

    HMW_ADD = {
        "title": Template("**Ajout d'un nouveau devoir - Étape $stepNum/$totalStep**\n"),

        "idle": Template("Veuillez préciser le nom du devoir que vous souhaitez créer \n\t - ex: 'Devoir maison #1'"),
        "name": Template("Veuillez préciser la matière du devoir que vous souhaitez créer \n\t - ex: 'Mathématiques', 'Physique'"),
        "date": Template("Veuillez préciser le statut du devoir que vous souhaitez créer \n\t - ex: 'À rendre', 'Optionnel'"),
        "status": Template("$hmwRecap"),
        "subject": Template("Veuillez préciser la date limite du devoir que vous souhaitez créer \n\tLe format de la date doit être le suivant '$dateFormat' - ex: $dateExample"),
        "document": Template("$hmwRecap")
    }

    HMW_EDIT = {
        "title": Template("**Édition d'un devoir - Étape $stepNum/$totalStep**\n"),
        "idle": Template("Veuillez préciser la matière du devoir que vous souhaitez éditer \n\t - ex: 'Mathématiques', 'Physique'"),
        "subject": Template("Veuillez sélectionner le devoir que vous souhaitez éditer dans la liste suivante:\n$hmwList"),
        "subjectSuggested": Template("\nLa matière '$subject' vous est suggérée, vous pouvez la sélectionner en cliquant sur la réaction $reac"),
        "name": Template("Vous avez sélectionné le devoir suivant:\n$hmwToDelete\n\nQuel champ souhaitez-vous éditer ?\n$fieldList"),

        "field": Template("- Cliquer sur la réaction $reac pour modifier le '$fieldElement' du devoir\n"),
    }

    HMW_DELETE = {
        "title": Template("**Suppression d'un devoir - Étape $stepNum/$totalStep**\n"),
        "idle": Template("Veuillez préciser la matière du devoir que vous souhaitez supprimer \n\t - ex: 'Mathématiques', 'Physique'"),
        "subject": Template("Veuillez sélectionner le devoir que vous souhaitez supprimer dans la liste suivante:\n$hmwList"),
        "name": Template("Vous avez sélectionné le devoir suivant:\n$hmwToDelete\n\nÊtes-vous sûr de vouloir supprimer ce devoir ?")
    }

    HMW_CONF = {
        "name": Template("+ Nom '$var' a bien été enregistré +"),
        "date": Template("+ Date '$var' a bien été enregistrée +"),
        "status": Template("+ Statut '$var' a bien été enregistré +"),
        "subject": Template("+ Matière '$var' a bien été enregistrée +"),
        "docUpdated": Template("+ Autorisation d'associer un fichier à ce devoir. +\nLes prochains fichiers que vous enverrez dans ce salon seront liés à ce devoir"),
        "docAdded": Template("+ Document '$docName' a bien été ajouté +\n"),
        "homeworkChosen": Template("+ Le devoir '$nomDevoir' a été sélectionné +\n"),

        "cancelledAction": Template("+ Dernière action '$oldVal' annulée +"),
        "cancelledDoc": Template("+ Les fichiers ne sont désormais plus autorisés +"),
        "wrongAction": Template("- Dernière action n'a pas pu être enregistrée : -\n-\t$errorMsg"),
        "dateError": Template("Erreur de format de date:\n\tLe format de la date doit être le suivant '$dateFormat' - ex: $date"),
        "dateInf": Template("Date antérieure:\n\tLa date entrée est trop ancienne"),
        "longName": Template("Le nom entré ne doit pas excéder $maxCar caractères\n\tVeuillez entrer un nom plus court"),

        'subjectError': Template("Aucune matière renseignée ne correspond à l'entrée '$val'. Liste des matières renseignées: -\n$subjectList"),
        'subjectChoice': Template("Matière '$sub' non renseignée, mais $nbChoice possibilité$plural1 existe$plural2: $subjectChoice  -"),

        "inDB": Template("- Ce devoir existe déjà en mémoire: -\n$inDBHmw"),
        "goodDB": Template("+ Nouvelle combinaison (nom = '$nameVar', matière = '$subjectVar') est valide +"),

        "backMessage": Template("+ Dernière modification ($lastModif) a bien été annulée +"),
        "cancelMessage": Template("+ $userAction du devoir a bien été annulé +"),

        "hmwAddedInDB": Template("+ Devoir enregistré dans la base de données +"),
        "hmwEditedInDB": Template("+ Devoir édité dans la base de données +"),
        "hmwDeletedInDB": Template("+ Devoir supprimé de la base de données +"),

        "hmwDeleted": Template("+ Devoir en cours de création a été supprimé +")
    }

    HMW_DESC = {
        "global": Template("Devoir de $subject : $nom\nStatut : $status\nPour le $date"),
        "docList": Template("\n$nbDoc document$plural associé$plural:"),
        "docName": Template("\n\t- $docName"),
        "docSuggestion": Template("\nAucun document associé\n\tSi vous souhaitez lier un document à ce devoir, utiliser la réaction correspondante ci-dessous")
    }

    @classmethod
    def stateDisplayer(cls, hmwUserAction, stateNum):
        if hmwUserAction == "hmwAdd":
            stateFR = ['Nom', 'Matiere', 'Date', 'Statut', 'Document']
        elif hmwUserAction == "hmwDelete":
            stateFR = ['Matière', 'Devoir']
        elif hmwUserAction == "hmwDelete":
            stateFR = ['Matière', 'Devoir']
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