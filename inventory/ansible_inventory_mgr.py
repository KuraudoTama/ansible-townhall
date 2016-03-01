from pymongo import MongoClient
import os
import json
from common.ansible_objects import AnsibleInventory, AnsibleInventoryEncoder
import common.settings as settings


class AnsibleInventoryManager(object):
    def __init__(self):
        self._inventories = dict()
        self._mongo_client = MongoClient(settings.get_mongodb_url())
        self._db = self._mongo_client['ansible_db']
        self._collection = self._db['inventories']
        self._rebuild_from_db()

    def list_inventories(self):
        return json.dumps(self._inventories, cls=AnsibleInventoryEncoder)

    def get_inventory(self, inventory_name):
        return json.dumps(self._inventories.get(inventory_name), cls=AnsibleInventoryEncoder)

    def add_inventory(self, inventory):
        self._inventories[inventory.name] = inventory
        self._save_to_db(inventory)

    def remove_inventory(self, inventory_name):
        self._remove_from_db(inventory_name)
        return json.dumps(self._inventories.pop(inventory_name), cls=AnsibleInventoryEncoder)

    def _save_to_db(self, inventory):
        inv_data = json.loads(json.dumps(inventory, cls=AnsibleInventoryEncoder))
        inv_data_from_db = self._collection.find_one({"name": inv_data.get('name')})
        if inv_data_from_db is None:
            self._collection.insert(inv_data)
        else:
            self._collection.replace_one({"name": inv_data.get('name')}, inv_data)

    def _remove_from_db(self, inventory_name):
        self._collection.delete_one({"name": inventory_name})

    def _rebuild_from_db(self):
        for inv_data in self._collection.find():
            inventory = AnsibleInventory(inv_data.get('name'), inv_data.get('path'))
            self._inventories[inventory.name] = inventory
