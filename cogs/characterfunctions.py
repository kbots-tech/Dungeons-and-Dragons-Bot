from datetime import datetime

BASE_URL = 'https://us-central1-dmtool-cad62.cloudfunctions.net/query?gameid={0}'
QUERY_URL = 'https://us-central1-dmtool-cad62.cloudfunctions.net/query?gameid={0}&type={1}&id={2}'

import aiohttp
import json
import pdfrw

import asyncio

class CharacterData():

    def __init__(self, gameid, id, player=None):
        self.session = aiohttp.ClientSession()
        self.fields = ["NO"]*334
        self.gameid = gameid
        self.id = id
        self.proficiencies = []
        self.urlCalls = 0
        self.player = player
        self.bonuses = [2,2,2,2,3,3,3,3,4,4,4,
                        4,5,5,5,5,6,6,6,6]

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
            basestats['cha'] = 10
        if 'con' in character['baseAttributes']:
            basestats['con'] = character['baseAttributes']['con']
        else:
            basestats['con'] = 10
        if 'dex' in character['baseAttributes']:
            basestats['dex'] = character['baseAttributes']['dex']
        else:
            basestats['dex'] = 10
        if 'int' in character['baseAttributes']:
            basestats['int'] = character['baseAttributes']['int']
        else:
            basestats['int'] = 10
        if 'str' in character['baseAttributes']:
            basestats['str'] = character['baseAttributes']['str']
        else:
            basestats['str'] = 10
        if 'wis' in character['baseAttributes']:
            basestats['wis'] = character['baseAttributes']['wis']
        else:
            basestats['wis'] = 10

        data['basestats'] = basestats
        data['class'] = await self.getClass(character)
        data['race'] = await self.getRace(character)
        data['background'] = await self.getBackground(character)
        data['inventory'] = await self.getInventory(character['inventory'])

        self.proficiencies.append(character['innateProperties']['savingThrows'])


        data['proficiencies'] = self.proficiencies
        data['lastupdate'] = "TODO"
        data['damage'] = character['damage_taken']


        for modifier in data['race']['features']:
            if modifier['name'] == "Ability Score Increase":
                for option in modifier['modifiers']:
                    data['basestats'][option['attribute']] += option['value']

        data['stats'] = await self.calcStats(data['basestats'], self.proficiencies, data)
        data['player'] = self.player

        data['ac'] = data['stats']['dexterity']
        if "Armor" in data['inventory']:
            ac = 0
            for armor in data['inventory']['Armor']:
                if ac < armor['ac']:
                    ac = armor['ac']
            data['ac'] += ac
        else:
            data['ac'] += 10


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

        if not "subraceid" in character:
            return data

        else:
            subrace = await self.fetchInfo(type="subrace", id=character['subraceid'])
            for feature in subrace['modifierInfo']['features']:
                data['features'].append(await self.featureBuilder(feature))
            return data

    async def getBackground(self, character):
        data = await self.fetchInfo(type="background", id=character['backgroundid'])
        background = {}
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
                print(item)

            else:
                features.append(await self.featureBuilder(item))
        background['features'] = features
        background['name'] = data['name']
        background['description'] = data['description']
        return background

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

                if "Weapon" in skill['name']:
                    skill['skills'] = {}
                    skill['skills'][skill['desc'][30:-3]] = skill['desc'][30:-3]
                    skill['type'] = "weapon"
                self.proficiencies.append(skill["skills"])
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
                itemdata['category'] = info['equipmentCategory']
            elif info['type'] == 'Armor':
                itemdata['ac'] = info['armorClass']
                itemdata['category'] = info['equipmentCategory']

            if info['type'] not in inventory:
                inventory[info['type']] = []
            inventory[info['type']].append(itemdata)

        return inventory

    async def getField(self, choice):
        if 'strength' in choice.lower():
            return 60
        elif 'dexterity' in choice.lower():
            return 61
        elif 'constitution' in choice.lower():
            return 62
        elif 'intelligence' in choice.lower():
            return 63
        elif 'wisdom' in choice.lower():
            return 64
        elif 'charisma' in choice.lower():
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
        else:
            return 0

    async def calcStats(self, data, proficiencies, level):

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

        levels = 0
        for classes in level['class']:
            levels += level['class'][classes]['level']

        for proficiency in proficiencies:
            for item in proficiency:
                if item == "str":
                    item = "strength"
                elif item == "dex":
                    item = "dexterity"
                elif item == "con":
                    item = "constitution"
                elif item == "int":
                    item = "intelligence"
                elif item == "wis":
                    item = "wisdom"
                elif item == "cha":
                    item = "charisma"

                if item in stats:
                    stats[item] += self.bonuses[levels]

        return stats

    async def calcValue(self, value):
        return int((value-10)/2)

    async def closeSession(self):
        await self.session.close()


    async def fillFields(self, data):
        self.fields[0] = data['name']
        levels = ""
        level = 0
        hpMax = 0
        hitDie = ""
        for classes in data['class']:
            levels += f"{data['class'][classes]['level']}, "
            hpMax += data['class'][classes]['hitdie']*data['class'][classes]['level']
            hitDie += f"d{data['class'][classes]['hitdie']}"
            level += data['class'][classes]['level']
        self.fields[14] = levels
        self.fields[15] = data['background']['name']
        self.fields[16] = data['player']
        self.fields[17] = data['name']
        self.fields[21] = data['basestats']['str']
        self.fields[22] = self.bonuses[level]
        self.fields[23] = data['ac']
        self.fields[24] = data['stats']['perception']
        self.fields[25] = data['race']['speed']['walk']
        self.fields[27] = data['stats']['strength']
        self.fields[28] = hpMax
        self.fields[29] = data['stats']['strength']
        self.fields[30] = data['basestats']['dex']
        self.fields[31] = hpMax-data['damage']
        self.fields[33] = data['stats']['dexterity']
        self.fields[36] = data['basestats']['con']
        self.fields[37] = level
        self.fields[41] = data['stats']['constitution']
        self.fields[45] = hitDie
        self.fields[47] = data['basestats']['int']
        self.fields[48] = data['stats']['dexterity']
        self.fields[49] = data['stats']['constitution']
        self.fields[50] = data['stats']['intelligence']
        self.fields[51] = data['stats']['wisdom']
        self.fields[52] = data['stats']['charisma']
        self.fields[53] = data['stats']['acrobatics']
        self.fields[54] = data['stats']['animal Handling']
        self.fields[55] = data['stats']['athletics']
        self.fields[56] = data['stats']['deception']
        self.fields[57] = data['stats']['history']
        self.fields[58] = data['stats']['insight']
        self.fields[59] = data['stats']['intimidation']
        self.fields[69] = data['stats']['intelligence']
        self.fields[73] = data['stats']['investigation']
        self.fields[74] = data['basestats']['wis']
        self.fields[77] = data['stats']['arcana']
        self.fields[79] = data['stats']['perception']
        self.fields[80] = data['stats']['wisdom']
        self.fields[81] = data['basestats']['cha']
        self.fields[82] = data['stats']['nature']
        self.fields[83] = data['stats']['performance']
        self.fields[84] = data['stats']['medicine']
        self.fields[85] = data['stats']['religion']
        self.fields[86] = data['stats']['stealth']
        self.fields[105] = data['stats']['persuasion']
        self.fields[106] = data['stats']['sleight of Hand']
        self.fields[107] = data['stats']['charisma']
        self.fields[108] = data['stats']['survival']
        self.fields[110] = data['stats']['perception']
        self.fields[333] = data['race']['name']
        features = ""
        for classes in data['class']:
            for feature in data['class'][classes]['features']:
                features += f"{feature['name']}\n"
        for feature in data['race']['features']:
            features += f"{feature['name']}\n"

        self.fields[118] = features



        languagelist = ["abyssal", "aquan", "auran", "celestial",
                     "common", "deep speech", "draconic",
                     "druidic", "dwarvish", "elvish",
                     "giant", "gnomish", "goblin",
                     "gnoll", "halfling", "ignan",
                     "infernal", "orc", "sylvan",
                     "terran", "undercommon"]
        languages = ""
        proficiencies = ""
        weapons = ""
        for group in data['proficiencies']:
            for item in group:
                if item in languagelist:
                    languages += f"{item}, "
                else:
                    proficiencies += f"{item}, "
                    if item == "str":
                        item = "strength"
                    elif item == "dex":
                        item = "dexterity"
                    elif item == "con":
                        item = "constitution"
                    elif item == "int":
                        item = "intelligence"
                    elif item == "wis":
                        item = "wisdom"
                    elif item == "cha":
                        item = "charisma"
                    key = await self.getField(item)
                    if key:
                        self.fields[key] = "Yes"
        self.fields[112] = f"Languages: {languages[:-2]}\nProficiencies: {proficiencies[:-2]}"

        self.fields[111] = data['wallet']['Copper']
        self.fields[113] = data['wallet']['Silver']
        self.fields[115] = data['wallet']['Gold']
        self.fields[114] = 0
        self.fields[116] = 0
        equipment = ""
        armor = ""
        weapons = ""

        for items in data['inventory']:
            if items == "Gear":
                for item in data['inventory'][items]:
                    equipment += f"{item['name']}, "
            elif items == "Armor":
                for item in data['inventory'][items]:
                    armor += f"{item['name']}, "
            elif items == "Shield":
                for item in data['inventory'][items]:
                    armor += f"{item['name']}, "
            elif items == "Weapon":
                for item in data['inventory'][items]:
                    weapons += f"{item['name']}, "

        self.fields[117] = f"Items: {equipment[:-2]}\n\nWeapons: {weapons[:-2]}\n\nArmor: {armor[:-2]}"

        weapons = data['inventory']['Weapon']

        if len(weapons) >= 1:
            self.fields[66] = weapons[0]['name']
            if "melee" in weapons[0]['category']:
                self.fields[67] = data['stats']['strength']
            elif "ranged" in weapons[0]['category']:
                self.fields[67] = data['stats']['dexterity']
            self.fields[68] = f"{weapons[0]['damage']} {weapons[0]['damageType']}"
        if len(weapons) >= 2:
            self.fields[70] = weapons[1]['name']
            if "melee" in weapons[1]['category']:
                self.fields[71] = data['stats']['strength']
            elif "ranged" in weapons[1]['category']:
                self.fields[71] = data['stats']['dexterity']
            self.fields[72] = f"{weapons[1]['damage']} {weapons[1]['damageType']}"
        if len(weapons) >= 3:
            self.fields[75] = weapons[2]['name']
            if "melee" in weapons[2]['category']:
                self.fields[76] = data['stats']['strength']
            elif "ranged" in weapons[2]['category']:
                self.fields[76] = data['stats']['dexterity']
            self.fields[78] = f"{weapons[2]['damage']} {weapons[2]['damageType']}"


        return await self.fill_pdf(self.fields)

    async def fill_pdf(self, fields, in_file=None, out_file=None):
        if in_file is None:
            in_file = pdfrw.PdfReader('5eSheet.pdf')
        if out_file is None:
            out_file = f'5eSheetOutput.pdf'
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