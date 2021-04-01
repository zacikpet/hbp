import click
from flask.cli import with_appcontext
from service import stats, update, fill, erase, classify, connect, classify_one


@click.command('stats')
@with_appcontext
def stats_command():
    statistics = stats()
    print(statistics)


@click.command('connect')
@with_appcontext
def connect_command():
    print('Connecting relevant articles...')
    connect()


@click.command('classify')
@with_appcontext
def classify_command():
    # Run NLP classifiers and recognizers on all articles in DB
    print('Classifying articles...')
    classify()


@click.command('classify_one')
@click.option('--id', type=str)
@with_appcontext
def classify_one_command(id):
    print('Classifying one article...')
    classify_one(id)
    print('Article Updated.')


@click.command('fill')
@with_appcontext
def fill_command():
    fill()

    print('Database filled.')


@click.command('update')
@click.option('--trigger', default='manual', type=str)
@with_appcontext
def update_command(trigger):
    update(trigger)
    print('Database updated.')


@click.command('erase')
@with_appcontext
def erase_command():
    print('Erasing database...')
    erase()
    print('Database erased.')

