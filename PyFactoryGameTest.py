


"""
class Sict(dict): #Sict means safedict.
  def __getitem__(self,key):
    try:
      return dict.__getitem__(self,key)
    except KeyError:
      return None


def sictify(thing):
  if isinstance(thing,dict):
    for key in thing.keys():
      if isinstance(thing[key],dict):
        thing[key] = Sict(thing[key])
      sictify(thing[key])
  elif type(thing) == list:
    for i in range(len(thing)):
      if isinstance(thing[i],dict):
        thing[i] = Sict(thing[i])
      sictify(thing[i])
"""


possibilities = [
    {"name":"zap","is_freestanding":False,"is_discrete":False},
    {"name":"crate","is_freestanding":True,"is_discrete":True,"storage":[]},
    {"name":"battery","is_freestanding":True,"is_discrete":True,"storage":[{"name":"zap"}]},
    {"name":"solar_panel","is_freestanding":True,"is_discrete":False,"cost":[{"name":"zap","scale":20}]}
  ]


world = [{"name":"battery","storage":[{"name":"zap","scale":100}]}]

"""
sictify(possibilities)
sictify(world)
"""

def genMatchInSeq(inputSeq,identifier,compareFun=(lambda x,y: x==y)):
  for item in inputSeq:
    if not isinstance(item,dict):
      continue
    skipItem = False
    for key in identifier.keys():
      if not compareFun(item[key],identifier[key]):
        skipItem = True
      if skipItem:
        break
      yield item

def genAllMembers(thing):
  if isinstance(thing,dict):
    yield thing
    for key in thing.keys():
      for member in genAllMembers(thing[key]):
        yield member
  elif type(thing) == list:
    yield thing
    for i in range(len(thing)):
      for member in genAllMembers(thing[i]):
        yield member

def genMatchInDeep(thing,identifier,compareFun=(lambda x,y: x==y)):
  return genMatchInSeq(genAllMembers(thing),identifier,compareFun=compareFun)

def augment(inputDict,fallbackDict,recursive=False):
  for key in fallbackDict.keys():
    if not key in inputDict.keys():
      inputDict[key] = fallbackDict[key]
    else:
      if recursive:
        if isinstance(inputDict[key],dict) and isinstance(fallbackDict[key],dict):
          augment(inputDict[key],fallbackDict[key])

def augmented(inputDict,fallbackDict):
  result = {}
  for key in inputDict.keys():
    result[key] = inputDict[key]
  for key in fallbackDict.keys():
    if not key in result.keys():
      result[key] = fallbackDict[key]
  return result

def redactKeys(inputDict,keysToRedact,recursive=True):
  for key in inputDict.keys():
    if key in keysToRedact:
      inputDict.__delitem__(key)
    else:
      if recursive:
        if isinstance(inputDict[key],dict):
          redact(inputDict[key],keysToRedact,recursive=True)

def getClone(thing):
  return eval(str(thing))

def subtractStructures(thing1,thing2,dryRun=False,symmetric=False): #this will likely break.
  augment(thing1,{"scale":1})
  augment(thing2,{"scale":1})
  assert isinstance(thing1,dict)
  assert isinstance(thing2,dict)
  for match in genMatchInDeep(thing1,thing2,compareFun=(lambda x,y: x==y or int in [type(x),type(y)])):
    assert isinstance(match,dict)
    if match["scale"] < thing2["scale"]:
      return False
    if not dryRun:
      match["scale"] -= thing2["scale"]
      if symmetric:
        thing2["scale"] = 0
    return True
    

keysNotAllowedInWorld = ["cost","is_freestanding","is_discrete","is_summoned"]
keysToRedactDuringSummon = ["cost"]


def tick():
  print("\n\n\nworld=" + str(world) + "\n\npossibilities=" + str(possibilities) + "\n\n")
  inputSentence = raw_input("tick>").replace(" ","")
  newWorldItems = []
  shouldContinue = processInputSentence(inputSentence,world,newWorldItems,outPrefix="your turn: ")
  for item in newWorldItems:
    redactKeys(item,keysNotAllowedInWorld)
    world.append(item)
  return shouldContinue


def processInputSentence(inputSentence,inputWorld,outputWorld,outPrefix="? "):
  inbar = []
  workbench = []
  outbar = []
  print(outPrefix+"the inbar, workbench, and outbar have been cleared.")
  print(outPrefix+"inputSentence is " + inputSentence + ".")
  if inputSentence == "q":
    return False
  inputWords = inputSentence.split("%")
  i = 0
  while i<len(inputWords):
    print(outPrefix+"processing word " + str(inputWords[i]) + ".")
    if inputWords[i] == "get":
      for item in genMatchInDeep(inputWorld,eval(inputWords[i+1])):
        inbar.append(item)
      print(outPrefix+"inbar is now " + str(inbar) + ".")
      i += 2
    elif inputWords[i] == "make":
      workbench.append(eval(inputWords[i+1]))
      print(outPrefix+"workbench is now " + str(workbench) + ".")
      i += 2
    elif inputWords[i] == "summon":
      newWorkbenchItem = eval(inputWords[i+1])
      #newWorkbenchItem["is_summoned"] = True
      redactKeys(newWorkbenchItem,keysToRedactDuringSummon)
      workbench.append(newWorkbenchItem)
      print(outPrefix+"workbench is now " + str(workbench) + ".")
      i += 2
    elif inputWords[i] == "exec":
      exec(inputWords[i+1])
      i += 2
    else:
      print(outPrefix+"the word is unknown and will be ignored.")
      i += 1
  #make workbench items:
  for i,workbenchItem in enumerate(workbench):
    isPossible = False
    for match in genMatchInSeq(possibilities,workbenchItem):
      augment(workbenchItem,getClone(match)) #never pull items directly from possibilities.
      isPossible = True
    if not isPossible:
      print(outPrefix+"the workbenchItem is impossible and won't be created.")
      continue
    if "cost" in workbenchItem.keys():
      costsAreCoverable = True
      for possibleResource in inbar:
        for costItem in workbenchItem["cost"]:
          costsAreCoverable *= subtractStructures(possibleResource,costItem,dryRun=True)
      print(outPrefix+"the costs " + ("can" if costsAreCoverable else "cannot") + " be covered.")
      if costsAreCoverable:
        for possibleResource in inbar:
          for costItem in workbenchItem["cost"]:
            subtractStructures(possibleResource,costItem,symmetric=True)
        outbar.append(workbenchItem)
        print(outPrefix+"item made.")
      else:
        print(outPrefix+"item not made.")
    else:
      print(outPrefix+"the finalItem has no cost, and will be created.")
      outbar.append(workbenchItem)
      workbench[i] = "removed workbench item at " + str(i)
  for i,outbarItem in enumerate(outbar):
    outputWorld.append(outbarItem)
    outbar[i] = "removed outbar item at " + str(i)
  return True


def main():
  while tick():
    pass


