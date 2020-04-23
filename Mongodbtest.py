from pymongo import MongoClient
import datetime

channel = {
    'chan_send_id': '696433109163573250',
    'chan_recv_id': '696433108899201158',
    'subject': 'si',
    'teacher_id': '122372446761254912',
}

client = MongoClient('localhost', 27017)
client.SchoolBot.send_recv_channels.insert_one(channel)
