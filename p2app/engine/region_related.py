import sqlite3
from p2app.events import *

def search_region(path, event):
    """Search region event"""
    try:
        region_code = event.region_code()
        local_code = event.local_code()
        name = event.name()
        if region_code is not None and local_code is not None and name is not None:
            yield from all_is_exist(path, region_code, local_code, name)
        if region_code is not None and local_code is not None and name is None:
            yield from name_is_not(path, region_code, local_code)
        if region_code is not None and local_code is None and name is not None:
            yield from local_code_is_not(path, region_code,name)
        if region_code is not None and local_code is None and name is None:
            yield from local_code_name_not(path, region_code)
        if region_code is None and local_code is not None and name is not None:
            yield from region_code_not(path, local_code, name)
        if region_code is None and local_code is not None and name is None:
            yield from region_code_name_not(path, local_code)
        if region_code is None and local_code is None and name is not None:
            yield from region_local_code_not(path, name)
    except Exception as error:
        yield ErrorEvent(str(error))


def all_is_exist(path, region_code, local_code, name):
    """Search by region_code, local_code, and name"""
    with sqlite3.connect(path) as data_connect:
        data_connect.execute("PRAGMA foreign_keys = ON;")
        command = '''SELECT region_id, continent_id, country_id, wikipedia_link, keywords FROM region WHERE region_code = ? AND local_code = ? AND name = ?;'''
        cursor = data_connect.execute(command, (region_code, local_code, name))
        result = cursor.fetchone()
        while result:
            result_region = Region(result[0], region_code, local_code, name, result[1], result[2], result[3], result[4])
            yield RegionSearchResultEvent(result_region)
            result = cursor.fetchone()

def name_is_not(path, region_code, local_code):
    """Search by region_code and local_code"""
    with sqlite3.connect(path) as data_connect:
        data_connect.execute("PRAGMA foreign_keys = ON;")
        command = '''SELECT region_id, name, continent_id, country_id, wikipedia_link, keywords FROM region WHERE region_code = ? AND local_code = ?;'''
        cursor = data_connect.execute(command, (region_code, local_code))
        result = cursor.fetchone()
        while result:
            result_region = Region(result[0], region_code, local_code, result[1], result[2], result[3], result[4], result[5])
            yield RegionSearchResultEvent(result_region)
            result = cursor.fetchone()

def local_code_is_not(path,region_code,name):
    """Search by region_code and name"""
    with sqlite3.connect(path) as data_connect:
        data_connect.execute("PRAGMA foreign_keys = ON;")
        command = '''SELECT region_id, local_code, continent_id, country_id, wikipedia_link, keywords FROM region WHERE region_code = ? AND name = ?;'''
        cursor = data_connect.execute(command, (region_code, name))
        result = cursor.fetchone()
        while result:
            result_region = Region(result[0], region_code, result[1], name, result[2], result[3], result[4], result[5])
            yield RegionSearchResultEvent(result_region)
            result = cursor.fetchone()


def local_code_name_not(path, region_code):
    """Search only by region_code"""
    with sqlite3.connect(path) as data_connect:
        data_connect.execute("PRAGMA foreign_keys = ON;")
        command = '''SELECT region_id, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region WHERE region_code = ?;'''
        cursor = data_connect.execute(command, (region_code, ))
        result = cursor.fetchone()
        while result:
            result_region = Region(result[0], region_code, result[1], result[2], result[3], result[4], result[5], result[6])
            yield RegionSearchResultEvent(result_region)
            result = cursor.fetchone()

def region_code_not(path, local_code, name):
    """Search by local_code and name"""
    with sqlite3.connect(path) as data_connect:
        data_connect.execute("PRAGMA foreign_keys = ON;")
        command = '''SELECT region_id, region_code, continent_id, country_id, wikipedia_link, keywords FROM region WHERE local_code = ? AND name = ?;'''
        cursor = data_connect.execute(command, (local_code, name))
        result = cursor.fetchone()
        while result:
            result_region = Region(result[0], result[1], local_code, name, result[2], result[3], result[4], result[5])
            yield RegionSearchResultEvent(result_region)
            result = cursor.fetchone()

def region_code_name_not(path, local_code):
    """Search only by local code"""
    with sqlite3.connect(path) as data_connect:
        data_connect.execute("PRAGMA foreign_keys = ON;")
        command = '''SELECT region_id, region_code, name, continent_id, country_id, wikipedia_link, keywords FROM region WHERE local_code = ?;'''
        cursor = data_connect.execute(command, (local_code, ))
        result = cursor.fetchone()
        while result:
            result_region = Region(result[0], result[1], local_code, result[2], result[3], result[4], result[5], result[6])
            yield RegionSearchResultEvent(result_region)
            result = cursor.fetchone()

def region_local_code_not(path, name):
    """Search only by name"""
    with sqlite3.connect(path) as data_connect:
        data_connect.execute("PRAGMA foreign_keys = ON;")
        command = '''SELECT region_id, region_code, local_code, continent_id, country_id, wikipedia_link, keywords FROM region WHERE name = ?;'''
        cursor = data_connect.execute(command, (name, ))
        result = cursor.fetchone()
        while result:
            result_region = Region(result[0], result[1], result[2], name, result[3], result[4], result[5], result[6])
            yield RegionSearchResultEvent(result_region)
            result = cursor.fetchone()


def load_region(path, region_id):
    """Load region event"""
    try:
        with sqlite3.connect(path) as data_connect:
            data_connect.execute("PRAGMA foreign_keys = ON;")
            command = '''SELECT region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region WHERE region_id = ?;'''
            cursor = data_connect.execute(command, (region_id, ))
            result = cursor.fetchone()
            if result is not None:
                result_region = Region(region_id, result[0], result[1], result[2], result[3], result[4], result[5], result[6])
                yield RegionLoadedEvent(result_region)
            else:
                yield ErrorEvent('Cannot load the region you chosen')
    except Exception as error:
        yield ErrorEvent(str(error))


def save_new_region(path, new_region):
    """Create and save a new region that you create"""
    try:
        with sqlite3.connect(path) as data_connect:
            data_connect.execute("PRAGMA foreign_keys = ON;")
            set_region_id = 'SELECT MAX(region_id) FROM region;'
            region_id = data_connect.execute(set_region_id).fetchone()[0] + 1
            command = '''INSERT INTO region (region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords) VALUES (?, ?, ?, ?, ?, ?, ?, ?);'''
            data_connect.execute(command, (region_id, new_region.region_code, new_region.local_code, new_region.name, new_region.continent_id, new_region.country_id, new_region.wikipedia_link, new_region.keywords))
            data_connect.commit()
            region_update = Region(region_id, new_region.region_code, new_region.local_code,
                                   new_region.name, new_region.continent_id, new_region.country_id, new_region.wikipedia_link, new_region.keywords)
            yield RegionSavedEvent(region_update)
    except sqlite3.IntegrityError as ex:
        if str(ex) == "UNIQUE constraint failed: region.region_code":
            yield SaveRegionFailedEvent("Region_code cannot be duplicated")
        elif str(ex) == "FOREIGN KEY constraint failed":
            yield SaveRegionFailedEvent("The Continent_id or country_id does not exist")
        else:
            yield SaveRegionFailedEvent(str(ex))


def save_region(path, edit_region):
    """Save region that already exist"""
    try:
        with sqlite3.connect(path) as data_connect:
            data_connect.execute("PRAGMA foreign_keys = ON;")
            command = '''UPDATE region SET name = ?, region_code = ?, local_code = ?, continent_id = ?, country_id = ?, wikipedia_link = ?, keywords = ? WHERE region_id = ?;'''
            data_connect.execute(command, (edit_region.name, edit_region.region_code, edit_region.local_code, edit_region.continent_id, edit_region.country_id, edit_region.wikipedia_link, edit_region.keywords, edit_region.region_id))
            data_connect.commit()
            region_update = Region(edit_region.region_id, edit_region.region_code, edit_region.local_code,
                                   edit_region.name, edit_region.continent_id, edit_region.country_id,
                                   edit_region.wikipedia_link, edit_region.keywords)
            yield RegionSavedEvent(region_update)
    except sqlite3.IntegrityError as ex:
        if str(ex) == "UNIQUE constraint failed: region.region_code":
            yield SaveRegionFailedEvent("Region_code cannot be duplicated")
        elif str(ex) == "FOREIGN KEY constraint failed":
            yield SaveRegionFailedEvent("The Continent_id or country_id does not exist")
        else:
            yield SaveRegionFailedEvent(str(ex))
