def getOutputCmakeName(name):
  return name.lower()

def getOutputSourcesName(name):
  return name.upper() + "_SOURCES"

def inBraces(string):
  return "${" + string + "}"

def isInBraces(string):
  return string[0] == '$' and string[1] == '{' and string[-1] == '}'

def modifyNameWithIndex(string, index):
  return string + "_" + str(index)

def capFirstLowerRest(string):
  return string[0].upper() + string[1:].lower()