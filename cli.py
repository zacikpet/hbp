import click
from flask.cli import with_appcontext
from service import HBPService
from database import mongo

service = HBPService(mongo)


@click.command('stats')
@with_appcontext
def stats_command():
    statistics = service.stats()
    print(statistics)


@click.command('connect')
@with_appcontext
def connect_command():
    print('Connecting relevant articles...')
    service.connect()


@click.command('classify')
@with_appcontext
def classify_command():
    # Run NLP classifiers and recognizers on all articles in DB
    print('Classifying articles...')
    service.classify()


@click.command('classify_one')
@click.option('--id', type=str)
@with_appcontext
def classify_one_command(id):
    print('Classifying one article...')
    service.classify_one(id)
    print('Article Updated.')


@click.command('fill')
@with_appcontext
def fill_command():
    service.fill()
    print('Database filled.')


@click.command('update')
@click.option('--trigger', default='manual', type=str)
@with_appcontext
def update_command(trigger):
    service.update(trigger)
    print('Database updated.')


@click.command('erase')
@with_appcontext
def erase_command():
    print('Erasing database...')
    service.delete_all_papers()
    print('Database erased.')
