class User():
  def __init__(self, fn=None, ln=None, pn=None):
    self.__first = fn
    self.__last = ln
    self.__phone = pn

  '''
  setFirst(self, f)

  param : f : first name string

  return : none

  desc : Sets the first name for user
  '''
  def setFirst(self, f):
    self.__first = f

  '''
  setLast(self, l)

  param : l : last name string
         
  return : none

  desc : Sets the last name for the user
  '''
  def setLast(self, l):
    self.__last = l

  '''
  setPhone(self, p)

  param : p : phone number string

  return : none

  desc : Sets the phone number for the user
  '''
  def setPhone(self, p):
    self.__phone = p

  '''
  getFirst(self)

  param : none

  return : first name string

  desc : Returns first name
  '''
  def getFirst(self):
    return self.__first

  '''
  getLast(self)

  param : none

  return : last name string

  desc : Returns last name
  '''
  def getLast(self):
    return self.__last

  '''
  getPhone(self)

  param : none

  return : phone number string

  desc : Returns phone number
  '''
  def getPhone(self):
    return self.__phone
