# TODO: remove after the database is connected to the project
# this is a dummy data file
import datetime

tasks = [
    {
        "uid": "7a6ea2d3-6e07-4a18-b387-977158df73e6",
        "title": "Training task #1 title",
    },
    {
        "uid": "6476a156-3df1-407a-b974-0b170e52c826",
        "title": "Training task #2 title",
    },
]

logs = [
    {
        "id": 1,
        "time": 0.5,
        "date": datetime.date(2022, 9, 10),
        "task": tasks[0],
    },
    {
        "id": 2,
        "time": 6,
        "date": datetime.date(2022, 9, 10),
        "task": tasks[1],
    },
    {
        "id": 3,
        "time": 2.5,
        "date": datetime.date(2022, 9, 11),
        "task": tasks[0],
    },
    {
        "id": 4,
        "time": 1.5,
        "date": datetime.date(2022, 9, 11),
        "task": tasks[1],
    },
    {
        "id": 5,
        "time": 2.5,
        "date": datetime.date(2022, 9, 12),
        "task": tasks[1],
    },
]


def get_log(pk: int):
    for log in logs:
        if log["id"] == pk:
            return log

    return
