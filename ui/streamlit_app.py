    st.subheader("🎮 Quick Matchmaking")
    host = st.text_input("Your Name", value=st.session_state.get("last_player", "Player"))
    omode = st.selectbox("Mode", ["501", "301", "701", "Cricket"])

    # Simple average input for skill matching
    player_avg = st.slider("Your Average (for matchmaking)", 20, 120, 55, step=5)

    if st.button("🚀 Quick Match (Skill-based)", type="primary", use_container_width=True):
        code = st.session_state.lobby.quick_match(host, omode, player_avg=player_avg)
        st.session_state.current_lobby_code = code
        st.success(f"Matched! Lobby: **{code}**")
        st.rerun()

    # Show current lobby with auto-refresh feel
    if st.session_state.get("current_lobby_code"):
        st.divider()
        st.subheader("📋 Your Lobby")

        info = st.session_state.lobby.get_lobby_info(st.session_state.current_lobby_code)

        if info:
            c1, c2 = st.columns(2)
            c1.metric("Lobby Code", info['code'])
            c2.metric("Status", info['status'].upper())

            st.write(f"**Host:** {info['host']} | **Mode:** {info['mode']}")
            st.write(f"**Players:** {len(info['players'])}/{info['max_players']}")

            if len(info['players']) >= 2:
                st.success("🎯 Lobby is ready! You can start playing.")

            colA, colB = st.columns(2)
            with colA:
                if st.button("🔄 Refresh Status"):
                    st.rerun()
            with colB:
                if st.button("❌ Leave Lobby"):
                    del st.session_state.current_lobby_code
                    st.rerun()
        else:
            st.warning("This lobby no longer exists.")
            if st.button("Clear"):
                del st.session_state.current_lobby_code
                st.rerun()

    st.divider()
    st.subheader("🔗 Join by Code")
    jcode = st.text_input("Enter Lobby Code")
    jname = st.text_input("Your Name", value=host, key="join_name2")
    if st.button("Join Lobby"):
        if st.session_state.lobby.join_by_code(jcode, jname):
            st.session_state.current_lobby_code = jcode.upper()
            st.success(f"Joined {jcode.upper()}!")
            st.rerun()
        else:
            st.error("Invalid code or lobby is full")