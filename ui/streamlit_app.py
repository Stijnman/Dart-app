    st.subheader("🎮 Create Match")
    host = st.text_input("Your Name", value=st.session_state.get("last_player", "Host"))
    omode = st.selectbox("Mode", ["501", "301", "701", "Cricket"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Quick Match", type="primary", use_container_width=True):
            code = st.session_state.lobby.quick_match(host, omode)
            st.session_state.current_lobby_code = code
            st.success(f"Joined/Created lobby: **{code}**")
            st.rerun()

    with col2:
        if st.button("Create Private Lobby", use_container_width=True):
            code = st.session_state.lobby.create_lobby(host, omode)
            st.session_state.current_lobby_code = code
            st.success(f"Private lobby created! Code: **{code}**")

    # Show current lobby status if in one
    if st.session_state.get("current_lobby_code"):
        st.divider()
        st.subheader("📋 Current Lobby")
        info = st.session_state.lobby.get_lobby_info(st.session_state.current_lobby_code)
        if info:
            st.write(f"**Code:** {info['code']}")
            st.write(f"**Host:** {info['host']}")
            st.write(f"**Mode:** {info['mode']}")
            st.write(f"**Players:** {len(info['players'])}/{info['max_players']}")
            st.write(f"**Status:** {info['status'].upper()}")

            if st.button("Leave Lobby"):
                del st.session_state.current_lobby_code
                st.rerun()
        else:
            st.warning("Lobby not found or expired.")
            if st.button("Clear Lobby"):
                del st.session_state.current_lobby_code

    st.subheader("🔗 Join Match")
    jcode = st.text_input("Join Code")
    jname = st.text_input("Your Name", value="Player", key="join_name")
    if st.button("Join"):
        if st.session_state.lobby.join_by_code(jcode, jname):
            st.session_state.current_lobby_code = jcode.upper()
            st.success(f"Joined lobby {jcode.upper()}!")
            st.rerun()
        else:
            st.error("Invalid code or lobby full")

    st.subheader("📋 Open Lobbies")
    lobbies = st.session_state.lobby.get_open_lobbies()
    if lobbies:
        for lob in lobbies:
            lc = st.columns([2,2,2,2,2])
            lc[0].write(lob['code'])
            lc[1].write(lob['host'])
            lc[2].write(lob['mode'])
            lc[3].write(lob['players'])
            if lc[4].button("Join", key=f"join_{lob['code']}"):
                if st.session_state.lobby.join_by_code(lob['code'], st.session_state.get("last_player", "Player")):
                    st.session_state.current_lobby_code = lob['code']
                    st.success(f"Joined {lob['code']}!")
                    st.rerun()
    else:
        st.caption("No open lobbies right now. Use Quick Match!")