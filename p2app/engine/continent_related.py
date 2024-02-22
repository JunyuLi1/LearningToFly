import sqlite3
from p2app.events import *


def check_database(path):
    """Check the validity of database"""
    try:
        with sqlite3.connect(path) as data_connect:
            cursor = data_connect.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('continent','country','region');")
            if cursor.fetchone():
                yield DatabaseOpenedEvent(path)
            else:
                yield DatabaseOpenFailedEvent('Database does not meet the requirement')
    except sqlite3.DatabaseError:
        yield DatabaseOpenFailedEvent('Not a sqlite3 database file')


def search(path, event):
    """Search continent event"""
    try:
        with sqlite3.connect(path) as data_connect:
            data_connect.execute("PRAGMA foreign_keys = ON;")
            continent_code = event.continent_code()
            name = event.name()
            if continent_code is not None and name is not None:
                impl_format = '''SELECT continent_id FROM continent WHERE continent_code = ? AND name = ?;'''
                continent_id = data_connect.execute(impl_format, (continent_code, name))
                result = continent_id.fetchone()
                if result is not None:
                    result_continent = Continent(result[0], continent_code, name)
                    yield ContinentSearchResultEvent(result_continent)
            if continent_code is not None and name is None:
                impl_format = '''SELECT continent_id, name FROM continent WHERE continent_code = ?;'''
                continent_id = data_connect.execute(impl_format, (continent_code, ))
                result = continent_id.fetchone()
                if result is not None:
                    result_continent = Continent(result[0], continent_code, result[1])
                    yield ContinentSearchResultEvent(result_continent)
            if continent_code is None and name is not None:
                impl_format = '''SELECT continent_id, continent_code FROM continent WHERE name = ?;'''
                continent_id = data_connect.execute(impl_format, (name, ))
                result = continent_id.fetchone()
                while result:
                    result_continent = Continent(result[0], result[1], name)
                    yield ContinentSearchResultEvent(result_continent)
                    result = continent_id.fetchone()
    except Exception as error:
        yield ErrorEvent(str(error))


def load(path, continent_id):
    """Load continent."""
    try:
        with sqlite3.connect(path) as data_connect:
            data_connect.execute("PRAGMA foreign_keys = ON;")
            impl_format = '''SELECT continent_code, name FROM continent WHERE continent_id = ?;'''
            continent = data_connect.execute(impl_format, (continent_id, ))
            result = continent.fetchone()
            if result is not None:
                result_continent = Continent(continent_id, result[0], result[1])
                yield ContinentLoadedEvent(result_continent)
            else:
                yield ErrorEvent('Cannot load the continent you chosen')
    except Exception as error:
        yield ErrorEvent(str(error))


def save_continent(path, save_continent):
    """Save continent which is already exist"""
    try:
        with sqlite3.connect(path) as data_connect:
            data_connect.execute("PRAGMA foreign_keys = ON;")
            command = '''UPDATE continent SET name = ?, continent_code = ? WHERE continent_id = ?;'''
            data_connect.execute(command, (save_continent.name, save_continent.continent_code, save_continent.continent_id, ))
            data_connect.commit()
            continent_updated = Continent(save_continent.continent_id, save_continent.continent_code, save_continent.name)
            yield ContinentSavedEvent(continent_updated)
    except sqlite3.IntegrityError:
        yield from save_failed()


def save_new(path, new_continent):
    """Save new continent into database"""
    try:
        with sqlite3.connect(path) as data_connect:
            data_connect.execute("PRAGMA foreign_keys = ON;")
            command_id = 'SELECT MAX(continent_id) FROM continent;'
            continent_id = data_connect.execute(command_id).fetchone()[0] + 1
            command = '''INSERT INTO continent (continent_id, continent_code, name) VALUES (?, ?, ?);'''
            data_connect.execute(command, (continent_id, new_continent.continent_code, new_continent.name, ))
            data_connect.commit()
            continent_updated = Continent(continent_id, new_continent.continent_code, new_continent.name)
            yield ContinentSavedEvent(continent_updated)
    except sqlite3.IntegrityError:
        yield from save_failed()


def save_failed():
    """Failed to save the continent"""
    yield SaveContinentFailedEvent('Continent_code cannot duplicate.')
