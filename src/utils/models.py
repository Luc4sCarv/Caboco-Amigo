from datetime import datetime
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """
    Define de onde veio o documento.
    Usar um Enum evita erros de digitação — ao invés de
    comparar strings como "obsidian" ou "Obsidian", usamos
    SourceType.OBSIDIAN em todo o código.
    """
    OBSIDIAN = "obsidian"
    PDF = "pdf"
    DOCX = "docx"
    EMAIL = "email"
    WEB = "web"


class Document(BaseModel):
    """
    Representa um documento bruto após ser lido da fonte.
    Por exemplo: uma nota .md lida do Obsidian, ou um PDF extraído.
    Ainda não foi dividido em pedaços — é o texto completo.
    """
    id: str                          # hash único do arquivo
    content: str                     # texto extraído e limpo
    source_type: SourceType          # de onde veio
    source_path: str                 # caminho ou URL de origem
    title: str = ""                  # título (nome do arquivo se não tiver)
    author: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: dict = Field(default_factory=dict)  # dados extras livres

    @property
    def short_source(self) -> str:
        """Retorna só o nome do arquivo, sem o caminho completo.
        Útil pra exibir nas respostas sem poluir com caminhos longos."""
        p = Path(self.source_path)
        return p.name if p.name else self.source_path[:60]


class Chunk(BaseModel):
    """
    Um pedaço de Document após o chunking.
    O RAG não trabalha com documentos inteiros — ele divide em
    pedaços menores (chunks) pra busca ser mais precisa.
    Ex: uma nota de 3000 palavras vira ~6 chunks de 500 palavras.
    """
    id: str
    document_id: str        # referência ao Document original
    content: str            # texto desse pedaço
    chunk_index: int        # posição dentro do documento (0, 1, 2...)
    source_type: SourceType
    source_path: str
    title: str = ""
    metadata: dict = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    """
    Um Chunk retornado pela busca semântica, com seu score.
    Score vai de 0 a 1 — quanto maior, mais relevante pra pergunta.
    """
    chunk: Chunk
    score: float    # relevância (0.0 a 1.0)
    rank: int = 0   # posição no ranking (0 = mais relevante)