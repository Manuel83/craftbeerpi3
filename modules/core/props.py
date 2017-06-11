class PropertyType(object):
    pass

class Property(object):
    class Select(PropertyType):
        def __init__(self, label, options):
            PropertyType.__init__(self)
            self.label = label
            self.options = options

    class Number(PropertyType):
        def __init__(self, label, configurable=False, default_value=0, unit=""):
            PropertyType.__init__(self)
            self.label = label
            self.configurable = configurable

    class Text(PropertyType):
        def __init__(self, label, configurable=False, default_value=""):
            PropertyType.__init__(self)
            self.label = label
            self.configurable = configurable

class StepProperty(Property):
    class Actor(PropertyType):
        def __init__(self, label):
            PropertyType.__init__(self)
            self.label = label
            self.configurable = True
    class Sensor(PropertyType):
        def __init__(self, label):
            PropertyType.__init__(self)
            self.label = label
            self.configurable = True
    class Kettle(PropertyType):
        def __init__(self, label):
            PropertyType.__init__(self)
            self.label = label
            self.configurable = True