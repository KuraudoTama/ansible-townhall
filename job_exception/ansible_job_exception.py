from exceptions import Exception

class InvalidContentTypeException(Exception):
    pass

class MissingKeyException(Exception):
    pass

class MissingDataException(Exception):
    pass

class InvalidDataTypeException(Exception):
    pass

class InvalidDataException(Exception):
    pass

class RecordNotFoundException(Exception):
    pass