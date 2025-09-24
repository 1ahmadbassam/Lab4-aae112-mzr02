"""
Factory module for the application's main data manager.

This module is responsible for selecting and instantiating the correct
data manager based on the `ENABLE_DATABASE` flag in the application's
configuration. It exports a single `data_manager` instance that conforms
to the `BaseDataManager` interface, abstracting away whether the application
is using in-memory or persistent database storage.
"""
from .dm.interface import DataError

DataError = DataError
"""Alias for DataError to be easily imported from this module."""

from .dm.memory import MemoryDataManager
from .dm.database import DatabaseDataManager
from config import ENABLE_DATABASE

if ENABLE_DATABASE:
    data_manager = DatabaseDataManager()
else:
    data_manager = MemoryDataManager()

data_manager = data_manager
"""
The singleton instance of the active data manager for the application.

This object will be either an instance of `DatabaseDataManager` or
`MemoryDataManager` depending on the configuration. All application logic
should use this manager to interact with the data layer.
"""
