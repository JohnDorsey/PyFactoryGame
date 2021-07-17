



def allTheSame(inputSeq):
  justStarted = True
  sharedValue = None
  for item in inputSeq:
    if justStarted:
      sharedValue = item
      justStarted = False
      continue
    if item != sharedValue:
      return False
  return True


possibilities = [
    {"name":"zap","is_freestanding":False,"is_discrete":False},
    {"name":"rock","is_freestanding":True,"is_discrete":False,"cost":[{"name":"stone","scale":1}]},
    {"name":"stone","is_freestanding":True,"is_discrete":False,"cost":[{"name":"rock","scale":0.5}]},
    {"name":"crate","is_freestanding":True,"is_discrete":True,"storage":[]},
    {"name":"battery","is_freestanding":True,"is_discrete":True,"storage":[{"name":"zap"}]},
    {"name":"solar_panel","is_freestanding":True,"is_discrete":False,"cost":[{"name":"zap","scale":20}]}
  ]


world = [{"name":"battery","storage":[{"name":"zap","scale":100}]},{"name":"rock","scale":1000000}]



keysNotAllowedInWorld = ["cost","is_freestanding","is_discrete","is_summoned"]
keysToRedactDuringSummon = ["cost"]


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
  print("subtractStructures is dangerous because its behavior is not obvious enough.")
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




def exploreParallelDicts(inputDicts,workerFun,allowedKeys=None,disallowedKeys=None,allowedTypes=None,disallowedTypes=None):
  assert len(inputDicts) > 0
  for inputDict in inputDicts:
    assert isinstance(inputDict,dict)
  if allowedKeys and disallowedKeys:
    for key in allowedKeys:
      if key in disallowedKeys:
        raise ValueError("allowedKeys and disallowedKeys overlap.")
  for key in inputDicts[0].keys():
    if allowedKeys:
      if not key in allowedKeys:
        continue
    if disallowedKeys:
      if key in disallowedKeys:
        continue
    if allowedTypes:
      if not type(inputDicts[0][key]) in allowedTypes:
        continue
    if disallowedTypes:
      if type(inputDicts[0][key]) in disallowedTypes:
        continue
    if not all((key in testDict.keys()) for testDict in inputDicts):
      continue
    if not allTheSame(type(testDict[key]) for testDict in inputDicts):
      continue
    print("running workerFun")
    workerFun(key,inputDicts)
    if all(isinstance(testDict[key],dict) for testDict in inputDicts):
      exploreParallelDicts([item[key] for item in inputDicts],workerFun,allowedKeys=allowedKeys,disallowedKeys=disallowedKeys,allowedTypes=allowedTypes,disallowedTypes=disallowedTypes)
      continue

def transferParallelDictValuesLeft(inputDicts,allowedKeys=None,disallowedKeys=None,allowedTypes=None,disallowedTypes=None):
  def transferFun(inputKey,subjects):
    assert len(subjects) > 1
    if type(subjects[0][inputKey]) not in [int,float]:
      return
    for otherSubject in subjects[1:]:
      print("before edit (subjects[0],otherSubject)="+str((subjects[0],otherSubject))+".")
      subjects[0][inputKey] += otherSubject[inputKey]
      otherSubject[inputKey] -= otherSubject[inputKey]
      print("after edit (subjects[0],otherSubject)="+str((subjects[0],otherSubject))+".")
  exploreParallelDicts(inputDicts,transferFun,allowedKeys=None,disallowedKeys=None,allowedTypes=None,disallowedTypes=None)

"""
def transferDictValues(destination,source,allowedKeys=None,disallowedKeys=None):
  assert isinstance(destination,dict)
  assert isinstance(source,dict)
  if allowedKeys and disallowedKeys:
    for key in allowedKeys:
      if key in disallowedKeys:
        raise ValueError("allowedKeys and disallowedKeys overlap.")
  for key in destination.keys():
    if allowedKeys:
      if not key in allowedKeys:
        continue
    if disallowedKeys:
      if key in disallowedKeys:
        continue
    if not key in source.keys():
      continue
    if not type(destination[key]) == type(source[key]):
      continue
    if isinstance(destination[key],dict) and isinstance(source[key],dict):
      transferMemberValues(destination[key],source[key],allowedKeys=allowedKeys,disallowedKeys=disallowedKeys)
      continue
    if isinstance(destination[key],list) and isinstance(source[key],list):
      print("transferDictValues: two values are both lists, but lists can't be handled.")
      continue
    if type(destination[key]) in [int,float] and type(source[key]) in [int,float]:
      destination[key] += source[key]
      source[key] -= source[key]
      continue
    print("transferDictValues: two items are the same type, but can't be handled.")
    continue
"""


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


