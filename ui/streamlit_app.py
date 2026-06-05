init_db(); init_db_v2()
defaults = {"game_started":False,"game":None,"voice":True,"entry":"per_dart","completed":False,
    "theme":"Dark Pro","spectator":False,"tv":False,"achievements":{},"career":None,
    "commentary":CommentaryEngine(),"lobby":LobbySystem(),"dgsl":DartsLiveFeatures("Player"),
        "audio":AudioEngine(AudioConfig(language=Language.ENGLISH)),
        "ui_engine":UIEnhancementEngine(),
        "auto_advance":False,
    "theme_sys":ThemeSystem(),"pro_sim":None}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v