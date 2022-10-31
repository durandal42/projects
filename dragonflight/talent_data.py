import collections

Talent = collections.namedtuple("Talent", "name points parents row col")

TALENT_TREES = {
  "Paladin": [
    # tier 1
    Talent("Lay on Hands", 1, [], 0, 1),
    Talent("Blessing of Freedom", 1, [], 0, 3),
    Talent("Hammer of Wrath", 1, [], 0, 5),

    Talent("Auras of the Resolute", 1, ["Lay on Hands", "Blessing of Freedom"], 1, 2),
    Talent("Auras of Swift Vengeance", 1, ["Blessing of Freedom", "Hammer of Wrath"], 1, 4),

    Talent("Repentance / Blinding Light", 1, ["Lay on Hands", "Auras of the Resolute"], 2, 1),
    Talent("Divine Steed", 1, ["Blessing of Freedom", "Auras of the Resolute", "Auras of Swift Vengeance"], 2, 3),
    Talent("Fist of Justice", 2, ["Hammer of Wrath", "Auras of Swift Vengeance"], 2, 5),

    Talent("Cleanse Toxins", 1, ["Repentance / Blinding Light"], 3, 0),
    Talent("Cavalier", 1, ["Divine Steed"], 3, 2),
    Talent("Seasoned Warhorse / Seal of the Templar", 1, ["Divine Steed"], 3, 4),
    Talent("Greater Judgment", 1, ["Fist of Justice"], 3, 6),

    # tier 2
    Talent("Holy Aegis", 2, ["Repentance / Blinding Light", "Cleanse Toxins"], 4, 1),
    Talent("Avenging Wrath", 1, ["Divine Steed", "Cavalier", "Seasoned Warhorse / Seal of the Templar"], 4, 3),
    Talent("Turn Evil", 1, ["Fist of Justice", "Seasoned Warhorse / Seal of the Templar", "Greater Judgment"], 4, 5),
    Talent("Rebuke", 1, ["Greater Judgment"], 4, 6),

    Talent("Golden Path", 1, ["Cleanse Toxins", "Holy Aegis"], 5, 0),
    Talent("Judgment of Light", 1, ["Holy Aegis"], 5, 1),
    Talent("Blessing of Sacrifice", 1, ["Holy Aegis", "Avenging Wrath"], 5, 2),
    Talent("Blessing of Protection", 1, ["Avenging Wrath", "Turn Evil"], 5, 4),
    Talent("Seal of Reprisal", 2, ["Turn Evil", "Rebuke"], 5, 6),

    Talent("Seal of Mercy", 2, ["Golden Path"], 6, 0),
    Talent("Afterimage", 1, ["Golden Path", "Judgment of Light", "Blessing of Sacrifice"], 6, 1),
    Talent("Sacrifice of the Just / Recompense", 1, ["Blessing of Sacrifice"], 6, 2),
    Talent("Unbreakable Spirit", 1, ["Blessing of Sacrifice", "Blessing of Protection"], 6, 3),
    Talent("Improved Blessing of Protection", 1, ["Blessing of Protection"], 6, 4),
    Talent("Incandescence / Touch of Light", 1, ["Blessing of Protection", "Seal of Reprisal"], 6, 5),

    # tier 3
    Talent("Seal of Clarity", 2, ["Seal of Mercy", "Afterimage"], 7, 0),
    Talent("Aspiration of Divinity", 2, ["Afterimage", "Sacrifice of the Just / Recompense"], 7, 1),
    Talent("Divine Purpose / Holy Avenger", 1, ["Sacrifice of the Just / Recompense", "Unbreakable Spirit", "Improved Blessing of Protection"], 7, 3),
    Talent("Obduracy", 1, ["Improved Blessing of Protection", "Incandescence / Touch of Light"], 7, 5),
    Talent("Hallowed Ground", 1, ["Incandescence / Touch of Light"], 7, 6),

    Talent("Of Dusk and Dawn", 1, ["Seal of Clarity", "Aspiration of Divinity"], 8, 1),
    Talent("Seal of Might", 2, ["Aspiration of Divinity", "Divine Purpose / Holy Avenger"], 8, 2),
    Talent("Seal of Alacrity", 2, ["Divine Purpose / Holy Avenger", "Obduracy"], 8, 4),
    Talent("Seal of the Crusader", 2, ["Obduracy", "Hallowed Ground"], 8, 5),

    Talent("Seal of Order", 1, ["Of Dusk and Dawn"], 9, 1),
    Talent("Sanctified Wrath / Seraphim", 1, ["Seal of Might", "Seal of Alacrity"], 9, 3),
    Talent("Zealot's Paragon", 1, ["Seal of the Crusader"], 9, 5),
  ],
}

def get_talents(tree):
    return TALENT_TREES[tree]
