# p2app/engine/main.py
#
# ICS 33 Spring 2023
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.
from .continent_related import *
from .country_related import *
from .region_related import *

class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self.path = None

    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""
        # This is a way to write a generator function that always yields zero values.
        # You'll want to remove this and replace it with your own code, once you start
        # writing your engine, but this at least allows the program to run.
        if isinstance(event, QuitInitiatedEvent):
            yield EndApplicationEvent()
        if isinstance(event, OpenDatabaseEvent):
            self.path = event.path()
            yield from check_database(self.path)
        if isinstance(event, CloseDatabaseEvent):
            yield DatabaseClosedEvent()
        if isinstance(event, StartContinentSearchEvent):
            yield from search(self.path, event)
        if isinstance(event, LoadContinentEvent):  # TODO: ErrorEvent
            continent_id = event.continent_id()
            yield from load(self.path, continent_id)
        if isinstance(event, SaveContinentEvent):
            continent = event.continent()
            yield from save_continent(self.path, continent)
        if isinstance(event, SaveNewContinentEvent):
            continent = event.continent()
            yield from save_new(self.path, continent)
        if isinstance(event, StartCountrySearchEvent):
            yield from search_country(self.path, event)
        if isinstance(event, LoadCountryEvent):
            country_id = event.country_id()
            yield from load_country(self.path, country_id)
        if isinstance(event, SaveNewCountryEvent):
            new_country = event.country()
            yield from save_new_country(self.path, new_country)
        if isinstance(event, SaveCountryEvent):
            edit_country = event.country()
            yield from save_country(self.path, edit_country)
        if isinstance(event, StartRegionSearchEvent):
            yield from search_region(self.path, event)
        if isinstance(event, LoadRegionEvent):
            region_id = event.region_id()
            yield from load_region(self.path, region_id)
        if isinstance(event, SaveNewRegionEvent):
            new_region = event.region()
            yield from save_new_region(self.path, new_region)
        if isinstance(event, SaveRegionEvent):
            edit_region = event.region()
            yield from save_region(self.path, edit_region)
