from flask_table import Table, Col

# Declare your table
class ItemTable(Table):
    name = Col('Config')
    description = Col('Value')

# Get some objects
class Item(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description
