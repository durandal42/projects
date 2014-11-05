import operator

ENEMY_LEVEL = 70

def item(armor=0, str=0, dex=0, int=0, vit=0, bonus_hp=0, bonus_armor=0,
         all_resist=0, physical_resist=0,cold_resist=0,fire_resist=0,
         lightning_resist=0, poison_resist=0, arcane_resist=0,
         min_damage=0, max_damage=0, aps=0, ias=0,
         crit_chance=0, crit_damage=0,
         loh=0, runspeed=0, sockets=0,set=None,
         mf=0, gf=0, cdr=0,
         block_chance=0,
         melee_reduced=0,ranged_reduced=0,elite_reduced=0):
    return {
        'armor':armor,
        'str':str, 'dex':dex, 'int':int, 'vit':vit,
        'bonus_hp':bonus_hp,
        'bonus_armor':bonus_armor,
        'all_resist':all_resist,
        'physical_resist':physical_resist, 'cold_resist':cold_resist,
        'fire_resist':fire_resist, 'lightning_resist':lightning_resist,
        'poison_resist':poison_resist, 'arcane_resist':arcane_resist,
        'min_damage':min_damage, 'max_damage':max_damage,
        'ias':ias, 'aps':aps,
        'crit_chance':crit_chance, 'crit_damage':crit_damage,
        'loh':loh,
        'runspeed':runspeed,
        'sockets':sockets,
        'set':set,
        'mf':mf, 'gf':gf,
        'cdr':cdr,
        'block_chance':block_chance,
        'specific_damage_reduced':melee_reduced+ranged_reduced+elite_reduced,
        }
DAMAGE = 'damage'
TOUGHNESS = 'toughness'

paragon_points = {
    'int':5,
    'dex':5,
    'str':5,
    'vit':5,
    'runspeed':0.5,
    'ias':0.002,
    'crit_chance':0.001,
    'crit_damage':0.01,
    'bonus_hp':0.005,
    'bonus_armor':0.005,
    'all_resist':5,
    'loh':5,
    'gf':1,
}

def compute_charsheet(passives, sources):
    stats = {}
    sets = {}
    for s in passives + sources:
        if type(s) == type([]): continue  # skip spec passives; they've already been included in passives
        for stat,value in s.iteritems():
            if not stat in stats:
                stats[stat] = 0
            if not value: continue 

            if stat in ['bonus_dodge', 'damage_reduced', 'cdr']:
                stats[stat] = 1.0 - (1.0 - stats[stat]) * (1.0 - value)
            elif stat is 'aps':
                if stats['aps'] > 0:
                    assert 'dual_wielding' not in stats
                    stats['dual_wielding'] = True
                    stats['aps'] = (stats['aps'] + value) / 2.0
                else:
                    stats['aps'] = value
            elif stat is 'set':
                if value:
                    if not value in sets: sets[value] = 0
                    sets[value] += 1
            else:
                stats[stat] += value

    if stats['aps'] == 0: stats['aps'] = 1  # base aps of 1 while unarmed
    if stats['min_damage'] == 0: stats['min_damage'] = 2  # base min_damage of 2 while unarmed
    if stats['max_damage'] == 0: stats['max_damage'] = 3  # base max_damage of 3 while unarmed

    if 'inna' in sets and sets['inna'] >= 2: stats['dex'] += 130

    if 'dex_scaling' in stats: stats['dex'] += 160*stats['sockets']
    if 'str_scaling' in stats: stats['str'] += 160*stats['sockets']
    if 'int_scaling' in stats: stats['int'] += 160*stats['sockets']

    stats['hp'] += 80 * stats['vit']  # TODO(dsloan): vit scaling per level
    stats['hp'] *= 1.0 + stats['bonus_hp']

    if 'seize_the_initiative' in stats: stats['armor'] += 0.5 * stats['dex']
    if 'nerves_of_steel' in stats: stats['armor'] += stats['vit']

    stats['armor'] += stats['str']
    stats['armor'] *= 1.0 + stats.get('bonus_armor', 0)

    stats['all_resist'] += stats['int'] * 0.1
    stats['physical_resist'] += stats['all_resist']
    stats['cold_resist'] += stats['all_resist']
    stats['fire_resist'] += stats['all_resist']
    stats['lightning_resist'] += stats['all_resist']
    stats['poison_resist'] += stats['all_resist']
    stats['arcane_resist'] += stats['all_resist']

    if 'bonus_resist' in stats:
        stats['physical_resist'] *= 1.0 + stats['bonus_resist']
        stats['cold_resist'] *= 1.0 + stats['bonus_resist']
        stats['fire_resist'] *= 1.0 + stats['bonus_resist']
        stats['lightning_resist'] *= 1.0 + stats['bonus_resist']
        stats['poison_resist'] *= 1.0 + stats['bonus_resist']
        stats['arcane_resist'] *= 1.0 + stats['bonus_resist']
        

    if 'one_with_everything' in stats:
        max_resist = max(stats['physical_resist'],
                         stats['cold_resist'],
                         stats['fire_resist'],
                         stats['lightning_resist'],
                         stats['poison_resist'],
                         stats['arcane_resist'])
        stats['physical_resist'] = max_resist
        stats['cold_resist'] = max_resist
        stats['fire_resist'] = max_resist
        stats['lightning_resist'] = max_resist
        stats['poison_resist'] = max_resist
        stats['arcane_resist'] = max_resist
        
    # TODO(dsloan): dodge formula is probably wrong as of 2.0
    stats['dodge'] = (min(70, max(0, stats['dex'] - 1000) * 0.01) +
                      min(10, max(0, stats['dex'] - 500) * 0.02) +
                      min(10, max(0, stats['dex'] - 100) * 0.025) +
                      min(10, stats['dex'] * 0.1)) / 100.0
    if 'bonus_dodge' in stats:
        stats['dodge'] = 1.0 - (1.0 - stats['dodge']) * (1.0 - stats['bonus_dodge'])
    if 'hold_your_ground' in stats:
        stats['dodge'] = 0

    stats[TOUGHNESS] = toughness(stats)

    if 'dual_wielding' in stats:
        stats['aps'] *= 1.15
        stats['min_damage'] *= 0.5
        stats['max_damage'] *= 0.5
    stats['aps'] *= 1.0 + stats['ias']
    stats['dps'] = (stats['min_damage'] + stats['max_damage']) / 2.0 * stats['aps']
    if 'bonus_dps' not in stats:
        stats['bonus_dps'] = 0.0
    if 'dex_scaling' in stats: stats['dps'] *= 1.0 + stats['dex'] * 0.01
    if 'str_scaling' in stats: stats['dps'] *= 1.0 + stats['str'] * 0.01
    if 'int_scaling' in stats: stats['dps'] *= 1.0 + stats['int'] * 0.01
    stats['dps'] *= 1.0 + stats['bonus_dps']
    stats['dps'] *= 1.0 + stats['crit_chance'] * stats['crit_damage']

    if stats.get('mf',0) > 300: stats['mf'] = 300
    if stats.get('gf',0) > 300: stats['gf'] = 300

    stats[DAMAGE] = stats['dps']

    return stats

def print_charsheet(stats):
    print 'ATTRIBUTES'
    print 'Strength:\t%d' % stats['str']
    print 'Dexterity:\t%d' % stats['dex']
    print 'Intelligence:\t%d' % stats['int']
    print 'Vitality:\t%d' % stats['vit']
    print
    print 'Damage:\t%d' % stats[DAMAGE]
    print 'Toughness:\t%d' % stats[TOUGHNESS]
    print
    print 'OFFENSE'
    if 'dex_scaling' in stats: print 'Damage Increased by Dexterity:\t%.2F%%' % stats['dex']
    if 'str_scaling' in stats: print 'Damage Increased by Strength:\t%.2F%%' % stats['str']
    if 'int_scaling' in stats: print 'Damage Increased by Intelligence:\t%.2F%%' % stats['int']
    print 'Damage Increased by Skills:\t%.2F%%' % stats['bonus_dps']
    print 'Attacks per Second:\t%.2F' % stats['aps']
    print 'Critical Hit Chance:\t%.2F%%' % (100.0 * stats['crit_chance'])
    print 'Critical Hit Damage:\t%.2F%%' % (100.0 * stats['crit_damage'])
    print
    print 'DEFENSE'
    print 'Armor:\t%d (%.2F%%)' % (stats['armor'], 100.0 * armor_dr(stats['armor']))
    print 'Block Amount:\tNYI'
    print 'Block Chance:\t%.2F%%' % (100.0 * stats['block_chance'])
    print 'Dodge Chance:\t%.2F%%' % (100.0 * stats['dodge'])
    print 'Physical Resistance:\t%d (%.2F%%)' % (stats['physical_resist'],
                                                 100.0 * resist_dr(stats['physical_resist']))
    print 'Cold Resistance:\t%d (%.2F%%)' % (stats['cold_resist'],
                                             100.0 * resist_dr(stats['cold_resist']))
    print 'Fire Resistance:\t%d (%.2F%%)' % (stats['fire_resist'],
                                             100.0 * resist_dr(stats['fire_resist']))
    print 'Lightning Resistance:\t%d (%.2F%%)' % (stats['lightning_resist'],
                                                  100.0 * resist_dr(stats['lightning_resist']))
    print 'Poison Resistance:\t%d (%.2F%%)' % (stats['poison_resist'],
                                               100.0 * resist_dr(stats['poison_resist']))
    print 'Arcane/Holy Resistance:\t%d (%.2F%%)' % (stats['arcane_resist'],
                                                    100.0 * resist_dr(stats['arcane_resist']))
    print
    print 'LIFE'
    print 'Maximum Life:\t%d' % stats['hp']
    print 'Total Life Bonus:\t%d' % stats['bonus_hp']
    print 'Life per Hit:\t%d' % stats['loh']

    print
    print 'ADVENTURE'
    print 'Gold Find:\t%d' % stats['gf']
    print 'Magic Find:\t%d' % stats['mf']

def armor_dr(armor, enemy_level=ENEMY_LEVEL):
    return armor / (armor + 50.0 * enemy_level)

def resist_dr(resist, enemy_level=ENEMY_LEVEL):
    return resist / (resist + 5.0 * enemy_level)

def toughness(stats):
    result = stats['hp']
    resists = [stats['physical_resist'],
               stats['cold_resist'],
               stats['fire_resist'],
               stats['lightning_resist'],
               stats['poison_resist'],
               stats['arcane_resist'],
               ]
    dr_sources = [armor_dr(stats['armor']),
                  resist_dr(sum(resists)/float(len(resists))),
                  stats.get('damage_reduced', 0.0),
                  stats.get('specific_damage_reduced', 0.0) * 0.5,
                  stats['dodge'],
                  ]
    for dr in dr_sources:
        result /= (1.0 - dr)
    return result

def item_contribution(passives, gear, metric=TOUGHNESS):
    contribution = {}
    charsheet = compute_charsheet(passives, gear.values())
    for slot in gear:
        gear_sans_item = [stats for loc,stats in gear.iteritems() if slot != loc]
        charsheet_sans_item = compute_charsheet(passives, gear_sans_item)
        contribution[slot] = charsheet[metric] - charsheet_sans_item[metric]
    sorted_contribution = sorted(contribution.iteritems(), key=operator.itemgetter(1))
    sorted_contribution.reverse()
    print 'item contribution to %s metric by slot:' % metric
    for slot,value in sorted_contribution:
        if not value: continue
        print '\t%s:\t%d' % (slot, value)

def stat_contribution(passives, gear, metric=TOUGHNESS):
    contribution = {}
    charsheet = compute_charsheet(passives, gear.values())
    for stat in paragon_points:
        if stat is 'aps': continue  # marginal aps not well handled
        gear_plus_stat = gear.values() + [{stat:paragon_points[stat]}]
        charsheet_plus_stat = compute_charsheet(passives, gear_plus_stat)
        contribution[stat] = charsheet_plus_stat[metric] - charsheet[metric]
    sorted_contribution = sorted(contribution.iteritems(), key=operator.itemgetter(1))
    sorted_contribution.reverse()
    print 'stat contribution to %s metric:' % metric
    for stat,value in sorted_contribution:
        if not value: continue
        print '\t%s:\t%d ppp' % (stat, value)

def compare(passives, gear, metric,
            slot, stats, print_result=True):
    if slot is 'ring':
        compare(passives, gear, metric, 'l_ring', stats, print_result)
        compare(passives, gear, metric, 'r_ring', stats, print_result)
        return
    if not slot in gear:
        print 'slot %s doesn\'t appear in gear.' % slot
        return None
    gear_alternative = gear.copy()
    gear_alternative[slot] = stats
    charsheet = compute_charsheet(passives, gear.values())
    charsheet_alternative = compute_charsheet(passives, gear_alternative.values())
    delta = charsheet_alternative[metric] - charsheet[metric]
    percent_delta = 100.0 * delta / charsheet[metric]
    if print_result:
        print '%s change of swapping %s:\t%d (%.2F%%)' % (metric, slot, delta, percent_delta)
    return percent_delta

CHARACTER = {
    'str': 7,
    'dex': 7,
    'int': 7,
    'vit': 7,
    'hp': 36,
    'crit_chance': 0.05,
    'crit_damage': 0.50,
    }
def MONK(n): return dict(DEX_HERO(n), damage_reduced=0.3)
def DEX_HERO(n):
    return {
        'str': n,
        'dex': 3*n,
        'int': n,
        'vit': 2*n,
        'hp': 4*n,
        'dex_scaling':True,
        }
def BARBARIAN(n): return STR_HERO(n)
def CRUSADER(n): return STR_HERO(n)
def STR_HERO(n):
    return {
#        'damage_reduced':0.3,
        'str': 3*n,
        'dex': n,
        'int': n,
        'vit': 2*n,
        'hp': 4*n,
        'str_scaling':True,
        }

ENCHANTRESS_POWERED_ARMOR = {'bonus_armor':0.03}
ENCHANTRESS_FOCUSED_MIND = {'ias':0.03}
SCOUNDREL_ANATOMY = {'crit_chance':0.03}

SEIZE_THE_INITIATIVE = {'seize_the_initiative':True}
ONE_WITH_EVERYTHING = {'one_with_everything':True}
MANTRA_OF_EVASION = {'bonus_dodge':0.15, 'bonus_armor':0.20}
MANTRA_OF_EVASION_ACTIVATION = {'bonus_dodge':0.15}
CRIPPLING_WAVE_CONCUSSION = {'damage_reduced':0.2}
DEADLY_REACH_KEEN_EYE = {'bonus_armor':0.5}
BREATH_OF_HEAVEN_BLAZING_WRATH = {'bonus_dps':0.15}
SWEEPING_WIND_CYCLONE = {'crit_damage':6*0.23}  # hack hack hack
FLEET_FOOTED = {'runspeed':10}

HOLD_YOUR_GROUND = {'hold_your_ground':True, 'block_chance':0.15}
LAWS_OF_VALOR = {'ias':0.08}

lintilla = {
    'passives': [
        CHARACTER,
        MONK(60),
        item(dex=20,
             crit_chance=0,crit_damage=0.04,
             all_resist=20,
             loh=49.5,
             ), #paragon hack
        SEIZE_THE_INITIATIVE,
        ONE_WITH_EVERYTHING,
        SWEEPING_WIND_CYCLONE,
        BREATH_OF_HEAVEN_BLAZING_WRATH,
        SCOUNDREL_ANATOMY,
        ],
    DAMAGE: {
        'helm': item(armor=361,str=95,dex=147,vit=87,arcane_resist=43,crit_chance=0.06,set='inna'),
        'neck': item(dex=163,arcane_resist=42,ias=9,loh=677),
        'should': item(armor=253,dex=218,all_resist=79),
        'chest': item(armor=687,str=45,dex=94,vit=165,arcane_resist=46,sockets=3),
        'gloves': item(armor=304,str=62,dex=112,arcane_resist=49,ias=9,crit_chance=0.075,mf=17),
        'waist': item(armor=183,dex=187,vit=187,all_resist=35),
        'legs': item(armor=414,dex=93,arcane_resist=34,ias=9,runspeed=12,crit_chance=0.01,sockets=2,set='inna'),
        'l_ring': item(dex=76,arcane_resist=36,ias=8,bonus_hp=12,crit_chance=0.03),
        'r_ring': item(dex=184,vit=204,ias=4,crit_damage=0.23,fire_resist=76),
        'boots': item(armor=439,dex=168,int=42,vit=119,arcane_resist=47,runspeed=12),
        'mhand': item(min_damage=1062,max_damage=1365,aps=1.14,dex=645),
        # 'ohand': item(min_damage=427,max_damage=957,int=114,aps=1.4,crit_damage=0.83+0.80),
        'wrist': item(armor=486,dex=113,vit=63,arcane_resist=42,crit_chance=0.06),
        'minion': item(gf=0,mf=13),
        },
}

dejah = { # TODO(dsloan): CDR
    'passives': [
        CHARACTER,
        CRUSADER(70),
        item(runspeed=10.5,
             all_resist=100,
             loh=1650.5), # paragon hack
        HOLD_YOUR_GROUND,
        ENCHANTRESS_FOCUSED_MIND,
        ENCHANTRESS_POWERED_ARMOR,
        LAWS_OF_VALOR,
        ],
    DAMAGE: {
        'helm': item(armor=684,str=749,vit=638,crit_chance=0.06,fire_resist=149,cdr=11.5),
        'neck': item(str=580,vit=590,crit_chance=0.09),
        'should': item(armor=602,str=409,vit=358,all_resist=90,cdr=7),
        'chest': item(armor=714,str=472,vit=481,all_resist=95,sockets=2),
        'gloves': item(armor=589,str=592,vit=527,crit_damage=0.3,crit_chance=0.095,arcane_resist=134),
        'wrist': item(armor=383,str=489,vit=480,crit_chance=0.06,lightning_resist=155),
        'waist': item(armor=828,str=470,vit=481,cdr=10),
        'legs': item(armor=737,str=495,vit=492,sockets=2),
        'l_ring': item(str=354,crit_damage=0.34,crit_chance=0.06,cdr=7,fire_resist=134),
        'r_ring': item(min_damage=52,max_damage=104,crit_damage=0.47,crit_chance=0.045,cdr=7,poison_resist=135),
        'boots': item(armor=944,str=484,vit=454,runspeed=11),
        'mhand': item(min_damage=2167,max_damage=2849,aps=1.15,str=976,crit_damage=1.2),
        'ohand': item(armor=2181,block_chance=0.14,str=596,crit_chance=0.10,cdr=7,poison_resist=134),
        },
}

def analyze(character, spec, metrics):
    passives = character['passives']
    gear = character[spec]
    print_charsheet(compute_charsheet(passives, gear.values()))
    for metric in metrics:
        item_contribution(passives, gear, metric)
    for metric in metrics:
        stat_contribution(passives, gear, metric)

def check_offset(character, spec, offspec, metric):
    passives = character['passives']
    gear = character[spec]
    for slot,stats in character[offset].iteritems():
        percent_delta = compare(passives, gear, metric,
                                slot, stats,
                                print_result=False)
        if percent_delta > 0:
            print "ALERT: offset item %s provides a %.2F%% increase to %s in %s mainset." % (
                slot, percent_delta, metric, spec)

def consider_upgrades(character, spec, metrics, slot, items):
    passives = character['passives']
    gear = character[spec]
    for item in items:
        for metric in metrics:
            compare(passives, gear, metric, slot, item)

analyze(dejah, DAMAGE, [DAMAGE, TOUGHNESS])
consider_upgrades(
    dejah, DAMAGE, [DAMAGE, TOUGHNESS],
    'ring',
    [
        
        ]
    )
