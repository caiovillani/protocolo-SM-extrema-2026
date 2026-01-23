# src/context_engine/context_cache.py

"""Sistema de cache para contexto processado.

Implementa cache YAML com invalidação por timestamp e hash de conteúdo.
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .context_models import StructuredDocument
from .context_reader import read_file


class CacheEntry:
    """Entrada de cache com metadados para validação."""

    def __init__(
        self,
        file_path: Path,
        content_hash: str,
        file_modified: datetime,
        cached_at: datetime,
        data: Dict[str, Any],
    ):
        """Inicializa entrada de cache.

        Args:
            file_path: Caminho do arquivo original
            content_hash: Hash MD5 do conteúdo
            file_modified: Data de modificação do arquivo
            cached_at: Data de criação do cache
            data: Dados serializados do documento
        """
        self.file_path = file_path
        self.content_hash = content_hash
        self.file_modified = file_modified
        self.cached_at = cached_at
        self.data = data

    def is_valid(self, file_path: Path) -> bool:
        """Verifica se cache ainda é válido.

        Compara timestamp de modificação do arquivo original.

        Returns:
            True se cache válido, False se arquivo foi modificado ou não existe.
        """
        try:
            file_stat = file_path.stat()
            file_modified = datetime.fromtimestamp(file_stat.st_mtime)
            return file_modified <= self.file_modified
        except (FileNotFoundError, OSError):
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionário."""
        return {
            'cache_metadata': {
                'file_path': str(self.file_path),
                'content_hash': self.content_hash,
                'file_modified': self.file_modified.isoformat(),
                'cached_at': self.cached_at.isoformat(),
            },
            'document': self.data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Deserializa de dicionário."""
        meta = data['cache_metadata']
        return cls(
            file_path=Path(meta['file_path']),
            content_hash=meta['content_hash'],
            file_modified=datetime.fromisoformat(meta['file_modified']),
            cached_at=datetime.fromisoformat(meta['cached_at']),
            data=data['document'],
        )


class ContextCache:
    """Gerenciador de cache de contexto."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Inicializa cache.

        Args:
            cache_dir: Diretório para armazenar cache (padrão: .context_cache)
        """
        self.cache_dir = cache_dir or Path(".context_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Estatísticas
        self._hits = 0
        self._misses = 0

    def _get_cache_path(self, file_path: Path) -> Path:
        """Gera caminho do arquivo de cache.

        Raises:
            ValueError: Se path traversal detectado.
        """
        # Hash do caminho para evitar conflitos
        path_hash = hashlib.md5(str(file_path.resolve()).encode()).hexdigest()[:16]
        safe_name = f"{file_path.stem}_{path_hash}.yaml"
        cache_path = (self.cache_dir / safe_name).resolve()

        # Validar que está dentro do cache_dir (previne path traversal)
        if not str(cache_path).startswith(str(self.cache_dir.resolve())):
            raise ValueError(f"Path traversal detectado: {file_path}")

        return cache_path

    def get(self, file_path: Path) -> Optional[CacheEntry]:
        """Recupera entrada do cache se válida.

        Args:
            file_path: Caminho do arquivo original

        Returns:
            CacheEntry se cache válido, None caso contrário
        """
        cache_path = self._get_cache_path(file_path)

        if not cache_path.exists():
            self._misses += 1
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # Validar estrutura básica do cache
            if not isinstance(data, dict):
                raise ValueError("Cache não é dicionário válido")
            if 'cache_metadata' not in data or 'document' not in data:
                raise ValueError("Cache com estrutura inválida")

            entry = CacheEntry.from_dict(data)

            if entry.is_valid(file_path):
                self._hits += 1
                return entry
            else:
                # Cache expirado
                self._misses += 1
                cache_path.unlink()
                return None

        except (yaml.YAMLError, ValueError, KeyError, TypeError):
            # Cache corrompido - remover
            self._misses += 1
            if cache_path.exists():
                cache_path.unlink()
            return None

    def put(self, file_path: Path, document: StructuredDocument) -> None:
        """Armazena documento no cache.

        Args:
            file_path: Caminho do arquivo original
            document: Documento processado
        """
        cache_path = self._get_cache_path(file_path)

        file_stat = file_path.stat()
        file_modified = datetime.fromtimestamp(file_stat.st_mtime)

        entry = CacheEntry(
            file_path=file_path,
            content_hash=document.metadata.hash_md5,
            file_modified=file_modified,
            cached_at=datetime.now(),
            data=document.to_dict(),
        )

        with open(cache_path, 'w', encoding='utf-8') as f:
            yaml.dump(entry.to_dict(), f, allow_unicode=True, default_flow_style=False)

    def invalidate(self, file_path: Path) -> bool:
        """Invalida cache de arquivo específico.

        Args:
            file_path: Caminho do arquivo

        Returns:
            True se cache foi removido, False se não existia
        """
        cache_path = self._get_cache_path(file_path)

        if cache_path.exists():
            cache_path.unlink()
            return True
        return False

    def clear(self) -> int:
        """Limpa todo o cache.

        Returns:
            Número de arquivos removidos
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.yaml"):
            cache_file.unlink()
            count += 1
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0

        cache_files = list(self.cache_dir.glob("*.yaml"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate,
            'entries': len(cache_files),
            'size_bytes': total_size,
            'size_mb': total_size / (1024 * 1024),
        }

    def reset_stats(self) -> None:
        """Reseta estatísticas."""
        self._hits = 0
        self._misses = 0


class CachedContextProcessor:
    """Processador de contexto com cache integrado."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        enable_cache: bool = True,
    ):
        """Inicializa processador com cache.

        Args:
            cache_dir: Diretório do cache
            enable_cache: Se True, usa cache
        """
        self._processor = None  # Lazy load para evitar import circular
        self.cache = ContextCache(cache_dir) if enable_cache else None
        self.enable_cache = enable_cache

    @property
    def processor(self):
        """Retorna processador (lazy load para evitar import circular)."""
        if self._processor is None:
            from .context_processor import ContextProcessor
            self._processor = ContextProcessor()
        return self._processor

    def process_file(self, file_path: Path, force_reload: bool = False) -> StructuredDocument:
        """Processa arquivo com cache.

        Args:
            file_path: Caminho do arquivo
            force_reload: Se True, ignora cache

        Returns:
            StructuredDocument processado
        """
        # Tentar cache
        if self.enable_cache and not force_reload:
            entry = self.cache.get(file_path)
            if entry:
                # Reconstruir documento do cache
                content, _, _ = read_file(file_path)
                return StructuredDocument.from_dict(entry.data, content)

        # Processar normalmente
        document = self.processor.process_file(file_path)

        # Salvar no cache
        if self.enable_cache:
            self.cache.put(file_path, document)

        return document

    def process_directory(
        self,
        directory: Path,
        patterns: Optional[List[str]] = None,
        force_reload: bool = False,
    ) -> Tuple[List[StructuredDocument], 'ContextIndex']:
        """Processa diretório com cache.

        Args:
            directory: Diretório a processar
            patterns: Padrões glob
            force_reload: Se True, ignora cache

        Returns:
            Tupla (documentos, índice)

        Raises:
            FileNotFoundError: Se diretório não existe.
        """
        from .context_models import ContextIndex

        if not directory.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {directory}")

        if patterns is None:
            patterns = ['*.md', '*.txt', '*.yaml', '*.yml', '*.py', '*.pdf']

        documents: List[StructuredDocument] = []
        index = ContextIndex()

        for pattern in patterns:
            for file_path in directory.rglob(pattern):
                if not file_path.is_file():
                    continue

                try:
                    doc = self.process_file(file_path, force_reload)
                    documents.append(doc)

                    for concept in doc.concepts:
                        index.add_concept(concept)

                except (FileNotFoundError, PermissionError, ValueError) as e:
                    print(f"Erro ao processar {file_path}: {e}")
                    continue

        return documents, index

    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        if self.cache:
            return self.cache.get_stats()
        return {'enabled': False}
