class InmetError(Exception):
    pass

class InvalidInmetFilenameError(InmetError):
    pass

class InvalidInmetSchemaError(InmetError):
    pass

class InmetYearMismatchError(InmetError):
    pass

class DuplicateInmetStationYearError(InmetError):
    pass

class EmptyInmetFileError(InmetError):
    pass

class InvalidInmetCsvStructureError(InmetError):
    pass

class InvalidInmetDateError(InmetError):
    pass

class InvalidInmetDateRangeError(InmetError):
    pass

class NoInmetFilesFoundError(InmetError):
    pass