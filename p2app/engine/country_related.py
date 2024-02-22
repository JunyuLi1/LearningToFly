import sqlite3
from p2app.events import *


def search_country(path, event):
    """Search country event"""
    try:
        with sqlite3.connect(path) as data_connect:
            data_connect.execute("PRAGMA foreign_keys = ON;")
            country_code = event.country_code()
            country_name = event.name()
            if country_code is not None and country_name is not None:
                command = '''SELECT country_id, continent_id, wikipedia_link, keywords FROM country WHERE country_code = ? AND name = ?;'''
                cursor = data_connect.execute(command, (country_code, country_name))
                result = cursor.fetchone()
                if result is not None:
                    result_country = Country(result[0], country_code, country_name, result[1], result[2], result[3])
                    yield CountrySearchResultEvent(result_country)
            if country_code is not None and country_name is None:
                command = '''SELECT country_id, name, continent_id, wikipedia_link, keywords FROM country WHERE country_code = ?;'''
                cursor = data_connect.execute(command, (country_code, ))
                result = cursor.fetchone()
                if result is not None:
                    result_country = Country(result[0], country_code, result[1], result[2], result[3], result[4])
                    yield CountrySearchResultEvent(result_country)
            if country_code is None and country_name is not None:
                command = '''SELECT country_id, country_code, continent_id, wikipedia_link, keywords FROM country WHERE name = ?;'''
                cursor = data_connect.execute(command, (country_name, ))
                result = cursor.fetchone()
                while result:
                    result_country = Country(result[0], result[1], country_name, result[2], result[3], result[4])
                    yield CountrySearchResultEvent(result_country)
                    result = cursor.fetchone()
    except Exception as error:
        yield ErrorEvent(str(error))


def load_country(path, country_id):
    """Load the country and then edit"""
    try:
        with sqlite3.connect(path) as data_connect:
            data_connect.execute("PRAGMA foreign_keys = ON;")
            command = '''SELECT country_code, name, continent_id, wikipedia_link, keywords FROM country WHERE country_id = ?;'''
            cursor = data_connect.execute(command, (country_id, ))
            result = cursor.fetchone()
            if result is not None:
                result_country = Country(country_id, result[0], result[1], result[2], result[3], result[4])
                yield CountryLoadedEvent(result_country)
            else:
                yield ErrorEvent('Cannot load the country you chosen')
    except Exception as error:
        yield ErrorEvent(str(error))


def save_new_country(path, save_country):
    """Create and save a new country"""
    try:
        if save_country.wikipedia_link is None:
            save_country = save_country._replace(wikipedia_link='')
        with sqlite3.connect(path) as data_connect:
            data_connect.execute("PRAGMA foreign_keys = ON;")
            set_country_id = 'SELECT MAX(country_id) FROM country;'
            country_id = data_connect.execute(set_country_id).fetchone()[0] + 1
            command = '''INSERT INTO country (country_id, country_code, name, continent_id, wikipedia_link, keywords) VALUES (?, ?, ?, ?, ?, ?);'''
            data_connect.execute(command, (country_id, save_country.country_code, save_country.name, save_country.continent_id, save_country.wikipedia_link, save_country.keywords))
            data_connect.commit()
            country_update = Country(country_id, save_country.country_code, save_country.name, save_country.continent_id,
                                     save_country.wikipedia_link, save_country.keywords)
            yield CountrySavedEvent(country_update)
    except sqlite3.IntegrityError as ex:
        if str(ex) == "UNIQUE constraint failed: country.country_code":
            yield SaveCountryFailedEvent("Country_code cannot be duplicated")
        elif str(ex) == "FOREIGN KEY constraint failed":
            yield SaveCountryFailedEvent("The Continent_id does not exist")
        else:
            yield SaveCountryFailedEvent(str(ex))


def save_country(path, save_country):
    """Save a country that is already exist"""
    try:
        if save_country.wikipedia_link is None:
            save_country = save_country._replace(wikipedia_link='')
        with sqlite3.connect(path) as data_connect:
            data_connect.execute("PRAGMA foreign_keys = ON;")
            command = '''UPDATE country SET name = ?, country_code = ?, continent_id = ?, wikipedia_link = ?, keywords = ? WHERE country_id = ?;'''
            data_connect.execute(command, (save_country.name, save_country.country_code, save_country.continent_id, save_country.wikipedia_link, save_country.keywords, save_country.country_id, ))
            data_connect.commit()
            country_update = Country(save_country.country_id, save_country.country_code, save_country.name,
                                     save_country.continent_id, save_country.wikipedia_link, save_country.keywords)
            yield CountrySavedEvent(country_update)
    except sqlite3.IntegrityError as ex:
        if str(ex) == "UNIQUE constraint failed: country.country_code":
            yield SaveCountryFailedEvent("Country_code cannot be duplicated")
        elif str(ex) == "FOREIGN KEY constraint failed":
            yield SaveCountryFailedEvent("The Continent_id does not exist")
        else:
            yield SaveCountryFailedEvent(str(ex))
