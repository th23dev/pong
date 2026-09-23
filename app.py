import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from ranking import salvar_recorde, RANK_PATH

USUARIOS_PATH = Path(__file__).with_name('usuarios.txt')
pong = components.declare_component('pong', path=str(Path(__file__).with_name('pong').resolve()))

st.set_page_config(page_title="PPT online")

if "loged" not in st.session_state:
    st.session_state.loged = False

if not st.session_state.loged:
    login_tab, register_tab = st.tabs(['Login', 'Registre-se'])

    with login_tab:
        with st.form("form_login"):
            email = st.text_input("Email")
            nome = st.text_input("nome")
            entrar = st.form_submit_button("Entrar")


        if entrar:
            if not email or not nome:
                st.error('Preencha todos os campos!')
            else:
                with open(USUARIOS_PATH, 'r', encoding='utf-8') as arquivo:
                    usuarios = [usuario.strip() for usuario in arquivo.readlines()]

                    if email in usuarios:
                        indice = usuarios.index(email)
                        if email == usuarios[indice] and nome == usuarios[indice + 1]:
                            st.session_state.loged = True
                            st.session_state.email = email
                            st.session_state.nome = nome
                            st.rerun()
                        else:
                            st.error('Email ou Nome errados!')
                    else:
                        st.error('Este usuário não está cadastrado')


    with register_tab:
        with st.form("form_register"):
            email = st.text_input("Email")
            nome = st.text_input("nome")
            entrar = st.form_submit_button("Cadastrar-se")


        if entrar:
            if not email or not nome:
                st.error('Preencha todos os campos!')
            else:
                with open(USUARIOS_PATH, 'r', encoding='utf-8') as arquivo:
                    usuarios = [usuario.strip() for usuario in arquivo.readlines()]

                if email in usuarios:
                    st.error('Usuário já cadastrado!')
                else:
                    with open(USUARIOS_PATH, 'a', encoding='utf-8') as arquivo:
                        arquivo.write(f'{email}\n{nome}\n')
                        st.success('Usuário cadastrado com sucesso!')
                    with open(RANK_PATH, 'a', encoding='utf-8') as rank:
                        rank.write(f'{email}\n0\n')

else:
    rank_tab, game_tab, profile_tab = st.tabs(['Rank', 'Jogo', 'Perfil'])

    with game_tab:
        st.subheader('Pongue')
        st.caption('Cada ponto seu soma 1. A partida acaba no primeiro ponto do bot. '
                   'O recorde é a maior pontuação em uma partida. '
                   'Reiniciar zera o placar, mas mantém seu recorde.')
        dados_rank = RANK_PATH.read_text(encoding='utf-8').splitlines()
        recordes = dict(zip(dados_rank[::2], dados_rank[1::2]))
        recorde = int(recordes.get(st.session_state.email, 0))
        pontuacao = pong(best=recorde, key=f'pong_{st.session_state.email}', default=None)
        if pontuacao is not None:
            try:
                if salvar_recorde(st.session_state.email, pontuacao):
                    st.rerun()
            except OSError:
                st.error('Não foi possível salvar o recorde. Verifique o acesso ao rank.txt.')

    with profile_tab:
        with st.container(border=True):
            st.write(f'Nome: {st.session_state.nome}')

            with open(RANK_PATH, 'r', encoding='utf-8') as arquivo_rank:
                dados = [dado.strip() for dado in arquivo_rank.readlines()]

                indice = dados.index(st.session_state.email)

                st.write(f'Pontuação: {dados[indice + 1]}')

            if st.button('Sair'):
                st.session_state.loged = False
                st.rerun()

    with rank_tab:
        with open(RANK_PATH, 'r', encoding='utf-8') as rank:
            dados = [dado.strip() for dado in rank.readlines()]

        pares = list(zip(dados[::2], dados[1::2]))
        pares.sort(key=lambda item: int(item[1]), reverse=True)

        with open(USUARIOS_PATH, 'r', encoding='utf-8') as arquivo:
            usuarios = [usuario.strip() for usuario in arquivo.readlines()]

        tabela = []
        for posicao, colocado in enumerate(pares, start=1):

            indice = usuarios.index(colocado[0])
            nome = usuarios[indice + 1]
            pontuacao = int(colocado[1])

            tabela.append({
                "Posição": posicao,
                "Nome": nome,
                "Pontuação": pontuacao,
            })

        st.table(tabela)
