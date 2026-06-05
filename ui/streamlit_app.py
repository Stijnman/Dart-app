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

            # Show players in lobby
            if info.get('players'):
                st.write("**Players in lobby:**")
                for p in info['players']:
                    st.write(f"- {p}")

            if len(info['players']) >= 2:
                st.success("🎯 Ready to play!")

                if st.button("▶️ Start Game from Lobby", type="primary", use_container_width=True):
                    # Create game from lobby players
                    pdata = [{"name": p} for p in info['players']]
                    start_game(pdata, info['mode'], "single_game", False, 5, "standard", False, False)
                    # Clear lobby after starting game
                    del st.session_state.current_lobby_code
                    st.rerun()

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