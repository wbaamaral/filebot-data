#!/usr/bin/env python3
"""
update_indices.py - Atualizador diário de índices de mídia para o FileBot.

Fontes públicas utilizadas:
- AniDB: https://anidb.net/api/anime-titles.dat.gz
- TMDb: https://files.tmdb.org/p/exports/movie_ids_MM_DD_YYYY.json.gz
- TMDb TV: https://files.tmdb.org/p/exports/tv_series_ids_MM_DD_YYYY.json.gz

Gera os arquivos compactados em lzma/xz com preset 9 extremo para o FileBot:
- data/anidb.txt.xz
- data/moviedb.txt.xz
- data/thetvdb.txt.xz
"""

import os
import sys
import gzip
import lzma
import json
import logging
import datetime
import urllib.request
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def download_stream(url, timeout=30):
    logging.info(f"Baixando: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(req, timeout=timeout)


def update_anidb():
    logging.info("--- Atualizando AniDB ---")
    url = "https://anidb.net/api/anime-titles.dat.gz"
    animes_primary = {}
    animes_aliases = defaultdict(list)

    try:
        with download_stream(url) as resp:
            with gzip.GzipFile(fileobj=resp) as gz:
                for line_bytes in gz:
                    line = line_bytes.decode("utf-8", errors="ignore").strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split("|")
                    if len(parts) < 4:
                        continue
                    aid, title_type, lang, title = parts[0], parts[1], parts[2], parts[3]
                    # Limpar espaços e tabs
                    title = title.replace("\t", " ").strip()
                    if not title:
                        continue

                    if title_type == "1":  # Primary title
                        animes_primary[aid] = title
                    elif title_type in ("2", "4"):  # Synonym ou Official
                        animes_aliases[aid].append(title)

        out_path = os.path.join(DATA_DIR, "anidb.txt.xz")
        logging.info(f"Processados {len(animes_primary)} animes. Salvando {out_path}...")
        
        # Ordenar por aid numérico
        sorted_aids = sorted(animes_primary.keys(), key=lambda x: int(x) if x.isdigit() else 9999999)
        with lzma.open(out_path, "wt", encoding="utf-8", preset=9 | lzma.PRESET_EXTREME) as out:
            for aid in sorted_aids:
                primary = animes_primary[aid]
                aliases = []
                seen = {primary.lower()}
                for a in animes_aliases.get(aid, []):
                    if a.lower() not in seen:
                        seen.add(a.lower())
                        aliases.append(a)
                line = "\t".join([aid, primary] + aliases)
                out.write(line + "\n")

        logging.info("AniDB atualizado com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao atualizar AniDB: {e}. Mantendo versão existente.")


def update_tmdb_movies():
    logging.info("--- Atualizando TMDb Movies (moviedb.txt.xz) ---")
    today = datetime.datetime.now(datetime.timezone.utc)
    dates_to_try = [today - datetime.timedelta(days=i) for i in range(3)]
    
    gz_resp = None
    for d in dates_to_try:
        date_str = d.strftime("%m_%d_%Y")
        url = f"http://files.tmdb.org/p/exports/movie_ids_{date_str}.json.gz"
        try:
            gz_resp = download_stream(url, timeout=20)
            logging.info(f"Encontrado dump diário TMDb: {url}")
            break
        except Exception:
            continue

    if not gz_resp:
        logging.warning("Não foi possível baixar o dump diário recente do TMDb. Mantendo versão existente.")
        return

    existing_movies = {}
    mov_path = os.path.join(DATA_DIR, "moviedb.txt.xz")
    if os.path.exists(mov_path):
        try:
            logging.info("Carregando base existente de moviedb.txt.xz...")
            with lzma.open(mov_path, "rt", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    parts = line.rstrip("\r\n").split("\t")
                    if len(parts) >= 4:
                        imdb_id, tmdb_id, year, name = parts[0], parts[1], parts[2], parts[3]
                        aliases = parts[4:] if len(parts) > 4 else []
                        existing_movies[tmdb_id] = (imdb_id, year, name, aliases)
            logging.info(f"{len(existing_movies)} filmes carregados da base existente.")
        except Exception as e:
            logging.warning(f"Erro ao ler moviedb.txt.xz atual: {e}")

    # Ler novo dump do TMDb e mesclar
    new_count = 0
    try:
        with gzip.GzipFile(fileobj=gz_resp) as gz:
            for line_bytes in gz:
                try:
                    data = json.loads(line_bytes.decode("utf-8", errors="ignore"))
                    tmdb_id = str(data.get("id"))
                    title = data.get("original_title", "").replace("\t", " ").strip()
                    if not tmdb_id or not title:
                        continue
                    if tmdb_id not in existing_movies:
                        existing_movies[tmdb_id] = ("0", "0", title, [])
                        new_count += 1
                except Exception:
                    continue
        logging.info(f"{new_count} novos filmes adicionados do TMDb.")

        # Regra de ordenação consistente por TMDb ID
        logging.info(f"Salvando {len(existing_movies)} filmes em {mov_path}...")
        sorted_ids = sorted(existing_movies.keys(), key=lambda x: int(x) if x.isdigit() else 99999999)
        with lzma.open(mov_path, "wt", encoding="utf-8", preset=9 | lzma.PRESET_EXTREME) as out:
            for tid in sorted_ids:
                imdb_id, year, name, aliases = existing_movies[tid]
                line = "\t".join([imdb_id, tid, year, name] + aliases)
                out.write(line + "\n")
        logging.info("TMDb Movies atualizado com sucesso!")
    except Exception as e:
        logging.error(f"Erro durante atualização de filmes TMDb: {e}")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    update_anidb()
    update_tmdb_movies()
    logging.info("Todos os processos de atualização diária foram concluídos!")


if __name__ == "__main__":
    main()
