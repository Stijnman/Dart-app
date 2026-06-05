    # === LOBBY CHAT SECTION ===
    if st.session_state.get("current_lobby_code"):
        st.divider()
        st.subheader("💬 Lobby Chat")

        lobby_code = st.session_state.current_lobby_code
        lobby = st.session_state.lobby.lobbies.get(
            st.session_state.lobby.join_codes.get(lobby_code)
        )

        if lobby:
            # Display chat history
            chat_container = st.container(height=250)
            with chat_container:
                for msg in lobby.get_chat_history():
                    timestamp = msg.get('time', '')[:16].replace('T', ' ')
                    st.markdown(f"**{msg['from']}** [{timestamp}]: {msg['msg']}")

            # Chat input
            chat_msg = st.text_input("Type a message", key="lobby_chat_input", placeholder="Say something...")
            col_send, col_clear = st.columns([3, 1])

            with col_send:
                if st.button("Send", key="send_chat") and chat_msg.strip():
                    lobby.send_chat(host, chat_msg.strip())
                    st.rerun()

            with col_clear:
                if st.button("🗑️ Clear", key="clear_chat"):
                    lobby.clear_chat()
                    st.rerun()
        else:
            st.warning("Lobby not found.")