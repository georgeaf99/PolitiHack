import boto.dynamodb2.exceptions as dynamo_exceptions
import boto.dynamodb2.table as dynamo_table
import copy

import jsonpickle

import json
import time
import uuid

import shared.common as common
import shared.config as config
import shared.service as service
import shared.version as version

from shared.common import Errors, PolitiHackException


##############################
# Global vars, consts, extra #
##############################

# Class of table names
table_prefix = config.store["dynamodb"]["table_prefix"]
class TableNames:
    CUSTOMERS       = table_prefix + "PolitiHack_Customers"
    VOTES           = table_prefix + "PolitiHack_Votes"

# Tables
customers       = dynamo_table.Table(TableNames.CUSTOMERS,       connection=service.dynamodb)
votes           = dynamo_table.Table(TableNames.VOTES,           connection=service.dynamodb)

# Use boolean for the tables
customers.use_boolean()
votes.use_boolean()


# Base class for all object models
class Model:
    def __init__(self, item):
        if not self._atts_are_valid(item._data):
            raise PolitiHackException(Errors.INVALID_DATA_PRESENT)

        self.item = item
        self.HANDLERS.migrate_forward_item(item)

    # Factory methods
    @classmethod
    def load_from_db(cls, primary_key, range_key=None, consistent=True):
        """Load an ite from dynamodb

        :param cls: The class to instantiate with the retrieved item
        :type cls: Subclass of model
        :param string primary_key: The primary key
        :param string range: (Optional) The secondary key
        :param bool consistent: (Optional) Whether or not the read should be consistent

        :returns: An instance of param `cls`
        """
        if not issubclass(cls, Model):
            raise ValueError("Class must be a subclass of Model")

        # None keys cause dynamodb exception
        if primary_key is None:
            return None

        item = None
        try:
            full_key = {}

            # If there is a range_key for this item, then one must be passed in
            if ("RANGE_KEY" in cls.__dict__) != (range_key is not None):
                raise PolitiHackException(Errors.DATA_NOT_PRESENT)
            elif range_key != None:
                # Now it is safe to set the range key if there is one
                full_key[cls.RANGE_KEY] = range_key

            full_key[cls.KEY] = key
            item = cls(cls.TABLE.get_item(consistent=consistent, **full_key))

            # Migrate the item forward if it is on an old version
            if item["version"] <= cls.VERSION:
                cls.HANDLERS.migrate_forward_item(item)
                if not item.save():
                    raise PolitiHackException(Errors.CONSISTENCY_ERROR)
        except dynamo_exceptions.ItemNotFound:
            raise PolitiHackException(cls.ITEM_NOT_FOUND_EX)

        return item

    @classmethod
    def load_from_data(cls, data):
        if not issubclass(cls, Model):
            raise ValueError("Class must be a subclass of Model")

        return cls(dynamo_table.Item(cls.TABLE, data))

    # Attribute access
    def __getitem__(self, key):
        return self.item[key]

    def get(self, key, default=None):
        return self.item[key] if key in self.item else default

    def __setitem__(self, key, val):
        if key in self.VALID_KEYS:
            self.item[key] = val
        else:
            raise ValueError("Attribute %s is not valid." % key)

    def __contains__(self, key):
        return key in self.item

    def update(self, atts):
        for key, val in atts.items():
            self[key] = val

    def _atts_are_valid(self, attributes):
        # Verify that the attributes passed in were valid
        for atr in attributes:
            if atr not in self.VALID_KEYS:
                return False

        return True

    def get_data(self, version=None):
        # Default to the latest version
        new_version = version if version is not None else self.VERSION

        self.HANDLERS.migrate_backward_item(self.item, new_version)
        data = copy.deepcopy(self.item._data)
        self.HANDLERS.migrate_forward_item(self.item)

        return data

    # Database Logic
    def save(self):
        # Defauult dynamodb behavior returns false if no save was performed
        if not self.item.needs_save():
            return True
        # Don't allow empty keys to be saved
        elif any([val == "" for val in self.get_data().values()]):
            raise PolitiHackException(Errors.INVALID_DATA_PRESENT)

        try:
            return self.item.partial_save()
        except dynamo_exceptions.ConditionalCheckFailedException:
            return False

    def create(self):
        # Don't allow empty keys to be saved
        if any((val == "" for val in self.get_data().values())):
            raise PolitiHackException(Errors.INVALID_DATA_PRESENT)

        if self.is_valid():
            return self.item.save()
        else:
            return False

    def delete(self):
        return self.item.delete()

    @classmethod
    def load_or_create(cls, primary_key, range_key=None, consistent=True):
        """Load the item from the DB or create a new one if none was found"""
        try:
            return cls.load_from_db(primary_key, range_key=range_key, consistent=consistent)
        except PolitiHackException as e:
            # If the error was not a not found exception, then it should be escalated
            if not e.error_type == cls.ITEM_NOT_FOUND_EX:
                raise e

        # Create a new item since none existed previously
        attributes = {
            cls.KEY: primary_key,
        }

        # Add a range key if one is present
        if range_key is not None:
            attributes[cls.RANGE_KEY] = range_key

        return cls.create_new(attributes)


class CFields:
    EMAIL = "email"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    PHONE_NUMBER = "phone_number"
    PROMPTED_WITH_BILL = "prompted_with_bill"
    SCOPED_BILL_ID = "scoped_bill_id"
    UUID = "uuid"
    VERSION = "version"
    ZIP_CODE = "zip_code"


class Customer(Model):
    FIELDS = CFields
    VALID_KEYS = set([getattr(CFields, attr) for attr in vars(CFields)
        if not attr.startswith("__")])
    TABLE_NAME = TableNames.CUSTOMERS
    TABLE = customers
    KEY = CFields.UUID
    MANDATORY_KEYS = set([CFields.VERSION, CFields.PHONE_NUMBER])
    VERSION = 1
    ITEM_NOT_FOUND_EX = Errors.CUSTOMER_DOES_NOT_EXIST

    # Initialize the migration handlers
    HANDLERS = version.MigrationHandlers(VERSION)

    def __init__(self, item):
        super().__init__(item)

    @staticmethod
    def create_new(attributes={}):
        # Default Values
        attributes[CFields.UUID] = common.get_uuid()
        attributes[CFields.VERSION] = Customer.VERSION

        return Model.load_from_data(Customer, attributes)

    def is_valid(self):
        if not self.MANDATORY_KEYS <= set(self.get_data()):
            return False

        # Check to that there is only one customer with this phone_number
        return customers.query_count(
            index="{0}-index".format(self[CFields.PHONE_NUMBER]),
            phone_number__eq=self[CFields.PHONE_NUMBER]) == 0


class VFields:
    BILL_ID = "bill_id"
    CUSTOMER_UUID = "customer_uuid"
    VERSION = "version"
    VOTE_RESULT = "vote_result"


class Votes(Model):
    FIELDS = VFields
    VALID_KEYS = set([getattr(VFields, attr) for attr in vars(VFields)
        if not attr.startswith("__")])
    TABLE_NAME = TableNames.VOTES
    TABLE = votes
    KEY = VFields.CUSTOMER_UUID
    RANGE_KEY = VFields.BILL_ID
    MANDATORY_KEYS = set([VFields.CUSTOMER_UUID, VFields.BILL_ID, VFields.VOTE_RESULT])
    VERSION = 1
    ITEM_NOT_FOUND_EX = Errors.VOTE_DOES_NOT_EXIST

    # Initialize the migration handlers
    HANDLERS = version.MigrationHandlers(VERSION)

    def __init__(self, item):
        super().__init__(item)

    @staticmethod
    def create_new(attributes={}):
        # Default Values
        attributes[VFields.VERSION] = Votes.VERSION

        return Model.load_from_data(Votes, attributes)

    def is_valid(self):
        return self.MANDATORY_KEYS <= set(self.get_data())
