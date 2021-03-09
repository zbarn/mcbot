class Browser():
  def __init__(self, opts=None, url=None, drive=None, t=None):
    self.__options = opts
    self.__URL = url
    self.__driver = drive
    self.__type = t

  def setOptions(self, o):
    self.__options = o

  def setUrl(self, u):
    self.__URL = u

  def setDriver(self, d):
    self.__driver = d

  def setType(self, t):
    self.__type = t

  def getOptions(self):
    return self.__options

  def getUrl(self):
    return self.__URL

  def getDriver(self):
    return self.__driver

  def getType(self): 
    return self.__type
