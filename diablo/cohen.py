

NERVES_OF_STEEL = {'nerves_of_steel': True}
TOUGH_AS_NAILS = {'bonus_armor': 0.25}
WAR_CRY = {'bonus_armor': 0.2, 'bonus_resist': 0.5}
WEAPONS_MASTER_MACE_AXE = {'crit_chance':10}
RUTHLESS = {'crit_chance':5, 'crit_damage':50}
BATTLE_RAGE_MARAUDER_RAGE = {'bonus_dps':0.3, 'crit_chance':3}
WRATH_BERSERKER_INSANITY = {'crit_chance':10, 'ias':25, 'bonus_dodge':0.20, 'bonus_dps':1.0}
LEAP_IRON_IMPACT = {'bonus_armor':3.0}

cohen = {
    'passives': [
        CHARACTER,
        BARBARIAN(60),
        ENCHANTRESS_POWERED_ARMOR,
        ],
    'tanking': {
        'passives': [
            NERVES_OF_STEEL,
            TOUGH_AS_NAILS,
            WAR_CRY,
            #LEAP_IRON_IMPACT,
            ],
        'helm': item(armor=640,str=71,int=29,vit=138,fire_resist=28),
        'neck': item(str=115,vit=123,arcane_resist=48,loh=316),
        'should': item(armor=355,str=86,vit=74,fire_resist=27,all_resist=73),
        'chest': item(armor=368,str=70,vit=149,fire_resist=30,all_resist=68),
        'gloves': item(armor=431,str=72,dex=51,vit=68,all_resist=69),
        'waist': item(armor=299,str=84,vit=74,all_resist=73),
        'legs': item(armor=394,str=72,int=73,vit=111,cold_resist=41,all_resist=66),
        'l_ring': item(str=76,vit=62,bonus_hp=4,crit_damage=24,loh=148),
        'r_ring': item(str=69,vit=58+34,fire_resist=25,loh=138),
        'boots': item(armor=311,str=77,vit=62,lightning_resist=47,all_resist=71),
        'mhand': item(aps=1.5, min_damage=316, max_damage=758, vit=134, loh=300),
        'ohand': item(armor=1129,all_resist=75),
        'wrist': item(armor=437,str=68,vit=73,arcane_resist=38,all_resist=63),
        },
    'dps': {
        'passives': [
            WEAPONS_MASTER_MACE_AXE,
            RUTHLESS,
            BATTLE_RAGE_MARAUDER_RAGE,
            #WRATH_BERSERKER_INSANITY,
            ],
        'helm': item(armor=640,str=71,int=29,vit=138,fire_resist=28),
        'neck': item(str=105,int=109,vit=83,physical_resist=27,crit_chance=4.5),
        'should': item(armor=355,str=86,vit=74,fire_resist=27,all_resist=73),
        'chest': item(armor=210,vit=91,str=34*3),
        'gloves': item(armor=147,str=108,vit=62,physical_resist=11),
        'waist': item(armor=138,str=95,vit=86),
        'legs': item(armor=347,str=59+34*2,vit=34,poison_resist=22),
        'l_ring': item(str=76,vit=62,bonus_hp=4,crit_damage=24,loh=148),
        'r_ring': item(min_damage=6,max_damage=6,str=70+34,int=51,vit=68,armor=94,crit_chance=2.5),
        'boots': item(armor=311,str=77,vit=62,lightning_resist=47,all_resist=71),
        'mhand': item(aps=1.5, min_damage=316, max_damage=758, vit=134),
        'ohand': item(armor=569,str=74+38,dex=43,int=45,vit=122),
        'wrist': item(armor=437,str=68,vit=73,arcane_resist=38,all_resist=63),
        },
}
