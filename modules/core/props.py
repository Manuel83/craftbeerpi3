class PropertyType(object):
    pass

class Property(object):
    class Select(PropertyType):
        def __init__(self, label, options, description=""):
            PropertyType.__init__(self)
            self.label = label
            self.options = options
            self.description = description

    class Number(PropertyType):
        def __init__(self, label, configurable=False, default_value=None, unit="", description=""):
            PropertyType.__init__(self)
            self.label = label
            self.configurable = configurable
            self.default_value = default_value
            self.description = description

    class Text(PropertyType):
        def __init__(self, label, configurable=False, default_value="", description=""):
            PropertyType.__init__(self)
            self.label = label
            self.configurable = configurable
            self.default_value = default_value
            self.description = description

    class Actor(PropertyType):
        def __init__(self, label, description=""):
            PropertyType.__init__(self)
            self.label = label
            self.configurable = True
            self.description = description

    class Sensor(PropertyType):
        def __init__(self, label, description=""):
            PropertyType.__init__(self)
            self.label = label
            self.configurable = True
            self.description = description

    class Kettle(PropertyType):
        def __init__(self, label, description=""):
            PropertyType.__init__(self)
            self.label = label
            self.configurable = True
            self.description = description


class StepProperty(Property):
    class Actor(PropertyType):
        def __init__(self, label, description=""):
            PropertyType.__init__(self)
            self.label = label
            self.configurable = True
            self.description = description
    class Sensor(PropertyType):
        def __init__(self, label, description=""):
            PropertyType.__init__(self)
            self.label = label
            self.configurable = True
            self.description = description
    class Kettle(PropertyType):
        def __init__(self, label, description=""):
            PropertyType.__init__(self)
            self.label = label
            self.configurable = True
            self.description = description
