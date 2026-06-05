    engine = DartGameEngine(mode=mode if mode.isdigit() or mode in ["x01"] else ml, players=pobjs,
        match_format=fm, bot_enabled=vs_bot, bot_difficulty=bot_lvl, variant=variant)