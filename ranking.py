from pathlib import Path
from threading import RLock
import os
import tempfile


RANK_PATH = Path(__file__).with_name('rank.txt')
_lock = RLock()


def salvar_recorde(email, pontuacao, caminho=RANK_PATH):
    """Atualiza somente o recorde desse jogador, preservando os demais."""
    if type(pontuacao) is not int or pontuacao < 0:
        return False
    caminho = Path(caminho)
    with _lock:
        dados = caminho.read_text(encoding='utf-8').splitlines()
        for indice in range(0, len(dados) - 1, 2):
            if dados[indice] != email:
                continue
            if pontuacao <= int(dados[indice + 1]):
                return False
            dados[indice + 1] = str(pontuacao)
            # A troca atômica evita que o ranking seja lido pela metade.
            temporario = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode='w', encoding='utf-8', dir=caminho.parent, delete=False
                ) as arquivo:
                    temporario = Path(arquivo.name)
                    arquivo.write('\n'.join(dados) + '\n')
                os.replace(temporario, caminho)
            finally:
                if temporario is not None:
                    temporario.unlink(missing_ok=True)
            return True
    return False
