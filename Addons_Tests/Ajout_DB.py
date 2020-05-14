from pymongo import MongoClient
import datetime

s_id = [696433109163573250, 696433109163573251, 696433109163573252, 696433109163573253, 696433109163573249]
r_id = [696433108899201158, 696433108899201159, 696433108899201160, 696433108899201161, 696433108899201157]
subject = ["si", "philo", "anglais", "isn", "physique"]


channel = {
        'name': 'sloth',
        'id': 122372446761254912,
        'subject': "matiere test"
    }

client = MongoClient('localhost', 27017)
client.SchoolBot.professeur.insert_one(channel)
