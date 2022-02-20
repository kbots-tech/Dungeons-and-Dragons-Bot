from datetime import datetime

BASE_URL = 'https://us-central1-dmtool-cad62.cloudfunctions.net/query?gameid={0}'
QUERY_URL = 'https://us-central1-dmtool-cad62.cloudfunctions.net/query?gameid={0}&type={1}&id={2}'

import aiohttp
import json
import pdfrw

import asyncio

class CharacterData():

    def __init__(self, gameid, id):
        self.session = aiohttp.ClientSession()
        self.fields = [""]*334
        self.gameid = gameid
        self.id = id
        self.proficiencies = []
        self.urlCalls = 0

    async def fetchInfo(self, type=None, id=None):
        self.urlCalls += 1
        if not type:
            async with self.session.get(BASE_URL.format(self.gameid)) as resp:
                return json.loads(await resp.text())
        else:
            if id is None:
                id = self.id
            async with self.session.get(QUERY_URL.format(self.gameid, type, id)) as resp:
                return json.loads(await resp.text())

    async def baseData(self):
        character = await self.fetchInfo('character')
        data = {}
        data['name'] = character['characterName']
        data['wallet'] = await self.getCurrency(character)
        print(character)

        basestats = {}

        if 'cha' in character['baseAttributes']:
            basestats['cha'] = character['baseAttributes']['cha']
        else:
            basestats['cha'] = 0
        if 'con' in character['baseAttributes']:
            basestats['con'] = character['baseAttributes']['con']
        else:
            basestats['con'] = 0
        if 'dex' in character['baseAttributes']:
            basestats['dex'] = character['baseAttributes']['dex']
        else:
            basestats['dex'] = 0
        if 'int' in character['baseAttributes']:
            basestats['int'] = character['baseAttributes']['int']
        else:
            basestats['int'] = 0
        if 'str' in character['baseAttributes']:
            basestats['str'] = character['baseAttributes']['str']
        else:
            basestats['str'] = 0
        if 'wis' in character['baseAttributes']:
            basestats['wis'] = character['baseAttributes']['wis']
        else:
            basestats['wis'] = 0

        data['basestats'] = basestats
        data['class'] = await self.getClass(character)
        data['race'] = await self.getRace(character)
        data['background'] = await self.getBackground(character)
        data['inventory'] = await self.getInventory(character['inventory'])

        data['stats'] = await self.calcStats(data['basestats'])
        data['proficiencies'] = self.proficiencies
        data['lastupdate'] = "TODO"
        print(self.proficiencies)
        print(self.urlCalls)
        return data

    async def getClass(self, character):
        data = {}
        for id in character['classes']:
            classData = await self.fetchInfo(type="class", id=id['classid'])
            info = {}

            info['level'] = id['level']

            data[classData['name']] = info
            data[classData['name']]['features'] = await self.classChoices(character['levelChoices'], classData, info['level'])
            data[classData['name']]['hitdie'] = classData['hit_die']
        return data

    async def getRace(self, character):

        data = {}

        raceData = await self.fetchInfo(type="race", id=character["raceid"])

        data['name'] = raceData['name']
        try:
            data['size'] = raceData['size']
        except KeyError:
            data['size'] = "n/a"
        try:
            data['speed'] = raceData['moveSpeeds']
        except KeyError:
            data['speed'] = "n/a"
        data['features'] = []

        for feature in raceData['modifierInfo']['features']:
            if 'options' in feature:
                choice = character['levelChoices'][feature['guid']]
                for item in choice:
                    for option in feature['options']:
                        if option['guid'] == item:
                            for modifier in option['modifiers']:
                                print("MODIFIER IS:")
                                print(modifier)
                                print("\n\n\n")
            elif 'modifiers' in feature:
                    stat = {}
                    skill = {}
                    stat['modifiers'] = []
                    stat['name'] = feature['name']
                    for feat in feature['modifiers']:
                        if feat['behavior'] == 'attribute':
                            skill = {"name": feat['name'],
                                     "attribute": feat['attribute'],
                                     "value": feat['value'],
                                     "type": "score"
                                     }
                        elif feat['behavior'] == 'proficiency':
                            skill = {
                                "name": feat['name'],
                                "skills": feat['skills'],
                                "desc": feat['description'],
                                "type": "proficiency"
                            }
                            self.proficiencies.append(feat["skills"])
                        elif feat['behavior'] == "conditionimmunity":
                            skill = {
                                "name": feat['name'],
                                "description": feat['description'],
                                "type": "immunity"
                            }
                        elif feat['behavior'] == "d20":
                            skill = {
                                "name": feat['name'],
                                "description": feat['description'],
                                "type": "advantage"
                            }
                        elif feat['behavior'] == "spell":
                            spell = await self.fetchInfo(id=feat['spell'],type="spell")

                            skill = {
                                "name": spell['name'],
                                "description": spell['description'],
                                "range": spell['range'],
                                "school": spell['school'],
                                "components": spell['components'],
                                "castingTime": spell['castingTime'],
                                "concentration": spell['concentration'],
                                "type": "spell"
                            }
                        elif feat['behavior'] == "resistance":
                            skill = {
                                "name": feat['name'],
                                "description": feat['description'],
                                "type": "resistance"
                            }
                        else:
                            print("FEAT IS:")
                            print(feat)
                            print("\n\n")
                            skill = feat
                        stat['modifiers'].append(skill)
                    data['features'].append(stat)
            else:
                data['features'].append(feature)

        if "darkvision" in raceData:
            data['darkvision'] = raceData['darkvision']
        else:
            data['darkvision'] = 0
        return data

    async def getBackground(self, character):
        data = await self.fetchInfo(type="background", id=character['backgroundid'])
        features = []
        choices = character['levelChoices']
        for item in data['modifierInfo']['features']:
            if "options" in item:
                try:
                    selections = choices[item['guid']]

                    for selection in selections:
                        for option in item['options']:
                            if option['guid'] == selection:
                                features.append(await self.featureBuilder(option))
                except KeyError:
                    print("Feature not set")

            else:
                features.append(await self.featureBuilder(item))
        return features

    async def classChoices(self, choices, classData, level):

        features = []

        levels = ["primary"]

        i = 1
        while i <= level:
            levels.append(f"level-{i}")
            i+=1

        for level in levels:


            stats = classData['levels'][level]
            for feature in stats['features']:
                if "options" in feature:
                    try:
                        selections = choices[feature['guid']]

                        for selection in selections:
                           for option in feature['options']:
                               if option['guid'] == selection:
                                features.append(await self.featureBuilder(option))
                    except KeyError:
                        print("Feature not set")

                else:
                    features.append(await self.featureBuilder(feature))
        return features

    async def featureBuilder(self, feature):

        stat = {}
        skill = {}
        stat['modifiers'] = []
        stat['name'] = feature['name']
        for feat in feature['modifiers']:
            if feat['behavior'] == 'attribute':
                skill = {"name": feat['name'],
                         "attribute": feat['attribute'],
                         "value": feat['value'],
                         "type": "score"
                         }
            elif feat['behavior'] == 'proficiency':
                skill = {
                    "name": feat['name'],
                    "skills": feat['skills'],
                    "desc": feat['description'],
                    "type": "proficiency"
                }
                self.proficiencies.append(feat["skills"])
            elif feat['behavior'] == "conditionimmunity":
                skill = {
                    "name": feat['name'],
                    "description": feat['description'],
                    "type": "immunity"
                }
            elif feat['behavior'] == "d20":
                skill = {
                    "name": feat['name'],
                    "description": feat['description'],
                    "type": "advantage"
                }
            elif feat['behavior'] == "spell":
                spell = await self.fetchInfo(id=feat['spell'],type="spell")

                skill = {
                    "name": spell['name'],
                    "description": spell['description'],
                    "range": spell['range'],
                    "school": spell['school'],
                    "components": spell['components'],
                    "castingTime": spell['castingTime'],
                    "concentration": spell['concentration'],
                    "type": "spell"
                }
            elif feat['behavior'] == "resistance":
                skill = {
                    "name": feat['name'],
                    "description": feat['description'],
                    "type": "resistance"
                }
            elif feat['behavior'] == "resource":
                pass
            else:
                print("FEAT IS:")
                print(feat)
                print("\n\n")
                skill = feat
            stat['modifiers'].append(skill)
        return stat

    async def getCurrency(self, character):
        wallet = {'Gold':0, 'Silver':0, 'Copper':0}
        for key in character['currency']:
            money = await self.fetchInfo('currency', key);
            wallet[money['name']] = character['currency'][key]['value']
        return wallet

    async def getInventory(self, items):
        inventory = {}
        for item in items:
            info = await self.fetchInfo(type="item", id=item)
            itemdata = {
                "name": info['name'],
                "weight": info['weight']
            }

            if info['type'] == 'Weapon':
                itemdata['damage'] = info['damage']
                itemdata['damageType'] = info['damageType']

            if info['type'] not in inventory:
                inventory[info['type']] = []
            inventory[info['type']].append(itemdata)

        return inventory

    async def getField(self, choice):
        if 'str' in choice.lower():
            return 60
        elif 'dex' in choice.lower():
            return 61
        elif 'con' in choice.lower():
            return 62
        elif 'int' in choice.lower():
            return 63
        elif 'wis' in choice.lower():
            return 64
        elif 'cha' in choice.lower():
            return 65
        elif 'acrobatics' in choice.lower():
            return 87
        elif 'animal' in choice.lower():
            return 88
        elif 'arcana' in choice.lower():
            return 89
        elif 'athletics' in choice.lower():
            return 90
        elif 'deception' in choice.lower():
            return 91
        elif 'history' in choice.lower():
            return 92
        elif 'insight' in choice.lower():
            return 93
        elif 'intimidation' in choice.lower():
            return 94
        elif 'investigation' in choice.lower():
            return 95
        elif 'medicine' in choice.lower():
            return 96
        elif 'nature' in choice.lower():
            return 97
        elif 'perception' in choice.lower():
            return 98
        elif 'performance' in choice.lower():
            return 99
        elif 'persuasion' in choice.lower():
            return 100
        elif 'religion' in choice.lower():
            return 101
        elif 'sleight' in choice.lower():
            return 102
        elif 'stealth' in choice.lower():
            return 103
        elif 'survival' in choice.lower():
            return 104

    async def calcStats(self, data):

        stats = {
            "strength": await self.calcValue(data['str']),
            "dexterity": await self.calcValue(data['dex']),
            "constitution": await self.calcValue(data['con']),
            "intelligence": await self.calcValue(data['int']),
            "wisdom": await self.calcValue(data['wis']),
            "charisma": await self.calcValue(data['cha']),
            "acrobatics": await self.calcValue(data['dex']),
            "animal Handling": await self.calcValue(data['wis']),
            "arcana": await self.calcValue(data['int']),
            "athletics": await self.calcValue(data['str']),
            "deception": await self.calcValue(data['cha']),
            "history": await self.calcValue(data['int']),
            "insight": await self.calcValue(data['wis']),
            "intimidation": await self.calcValue(data['cha']),
            "investigation": await self.calcValue(data['int']),
            "medicine": await self.calcValue(data['wis']),
            "nature": await self.calcValue(data['int']),
            "perception": await self.calcValue(data['wis']),
            "performance": await self.calcValue(data['cha']),
            "persuasion": await self.calcValue(data['cha']),
            "religion": await self.calcValue(data['int']),
            "sleight of Hand": await self.calcValue(data['dex']),
            "stealth": await self.calcValue(data['dex']),
            "survival": await self.calcValue(data['wis']),
        }


        return stats

    async def calcValue(self, value):
        return int(value/7)

    async def closeSession(self):
        await self.session.close()


    async def fillFields(self, data):
        return True

    async def fill_pdf(fields, in_file=None, out_file=None):
        if in_file is None:
            in_file = pdfrw.PdfReader('./5eSheet.pdf')
        if out_file is None:
            out_file = f'./5eSheetOutput.pdf'
        in_file.Root.AcroForm.update({pdfrw.PdfName.NeedAppearances: True})
        for i in range(len(in_file.Root.AcroForm.Fields)):
            item = in_file.Root.AcroForm.Fields[i]
            if item.FT == '/Btn':
                if fields[i] != 'NO':
                    item.AS = 'Yes'
            else:
                if fields[i] != 'NO':
                    item.V = str(fields[i])
        else:
            pdfrw.PdfWriter().write(out_file, in_file)
        return out_file







async def main():
    retrieval = CharacterData("LittleEpicTemperamentalElf", "0a45ceaa-3c01-4b70-b288-f6ebce564980")
    data = await retrieval.baseData()
    pdf = await retrieval.fillFields(data)
    await retrieval.closeSession()
    print(data)


newfeature = asyncio.run(main())