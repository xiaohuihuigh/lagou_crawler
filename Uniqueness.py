import uuid
class Uniqueness(object):

    def __init__(self):
        pass

    @staticmethod
    def generateUUID(name, namespace=uuid.NAMESPACE_DNS):
        return uuid.uuid5(namespace, name)

    @staticmethod
    def combineNames(*strlist):
        return ''.join([str(sl) for sl in strlist])

    @classmethod
    def gerUUID(cls, *strlist):
        name = cls.combineNames(*strlist)
        return str(cls.generateUUID(name))


if __name__ == '__main__':
    pass
