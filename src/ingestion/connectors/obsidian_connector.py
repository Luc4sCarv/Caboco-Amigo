import hashlib
from datetime import datetime
from pathlib import Path

from src.utils.models import Document, SourceType


def _gerar_id(caminho: Path) -> str:
    """
    Gera um ID único baseado no caminho do arquivo.
    Usamos MD5 do caminho — não é criptografia, só um jeito
    de ter um ID curto e único pra cada arquivo.
    """
    return hashlib.md5(str(caminho).encode()).hexdigest()


def _extrair_frontmatter(conteudo: str) -> tuple[dict, str]:
    """
    Frontmatter é o bloco no topo de arquivos .md com metadados.
    Exemplo:
        ---
        title: Minha Nota
        tags: jogos, rpg
        ---
        Conteúdo da nota aqui...

    Esta função separa esse bloco do conteúdo real.
    Se não tiver frontmatter, retorna dict vazio e o conteúdo inteiro.
    """
    meta = {}

    if not conteudo.startswith("---"):
        return meta, conteudo

    fim = conteudo.find("---", 3)
    if fim == -1:
        return meta, conteudo

    bloco = conteudo[3:fim].strip()
    corpo = conteudo[fim + 3:].strip()

    for linha in bloco.splitlines():
        if ":" in linha:
            chave, _, valor = linha.partition(":")
            meta[chave.strip()] = valor.strip()

    return meta, corpo


def carregar_vault(caminho_vault: Path) -> list[Document]:
    """
    Lê todos os arquivos .md de uma pasta (e subpastas)
    e retorna uma lista de Documents prontos pra serem
    processados pelo chunker.
    """
    if not caminho_vault.exists():
        print(f"Pasta não encontrada: {caminho_vault}")
        return []

    arquivos = list(caminho_vault.rglob("*.md"))
    print(f"Encontrados {len(arquivos)} arquivos .md em {caminho_vault}")

    documentos = []

    for arquivo in arquivos:
        try:
            conteudo_raw = arquivo.read_text(encoding="utf-8", errors="replace")
            meta, corpo = _extrair_frontmatter(conteudo_raw)

            if not corpo.strip():
                continue  # pula arquivos vazios

            stat = arquivo.stat()

            doc = Document(
                id=_gerar_id(arquivo),
                content=corpo,
                source_type=SourceType.OBSIDIAN,
                source_path=str(arquivo),
                title=meta.get("title", arquivo.stem),
                author=meta.get("author", ""),
                created_at=datetime.fromtimestamp(stat.st_ctime),
                updated_at=datetime.fromtimestamp(stat.st_mtime),
                metadata={
                    "tags": meta.get("tags", ""),
                },
            )
            documentos.append(doc)

        except Exception as e:
            print(f"Erro ao ler {arquivo.name}: {e}")

    print(f"Carregados {len(documentos)} documentos")
    return documentos