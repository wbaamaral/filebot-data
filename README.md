# FileBot Data & Scripts (Comunidade / Offline)

Repositório com índices de dados e pacotes de scripts independentes para o **FileBot**.

Este repositório substitui a infraestrutura proprietária original (`app.filebot.net`), oferecendo:
- **100% de Autonomia**: Sem telemetria, bloqueios ou verificações de licença externa.
- **Privacidade**: Nenhuma informação da sua biblioteca é enviada a servidores de terceiros.
- **Alta Disponibilidade**: Hospedado no GitHub e servido diretamente via GitHub Raw ou GitHub Pages.

---

## 📁 Estrutura de Arquivos

* `data/`
  * `thetvdb.txt.xz`: Índice e mapeamento de séries, títulos alternativos e aliases do TheTVDB.
  * `moviedb.txt.xz`: Índice de filmes com mapeamento TMDb, IMDb, títulos e aliases.
  * `anidb.txt.xz`: Índice de animes com sinônimos e títulos originais.
  * `osdb.txt.xz`: Mapeamentos do OpenSubtitles.
  * `series-mappings.txt.xz`: Expressões regulares para mapeamento de séries.
  * `release-groups.txt.xz`: Dicionário de grupos de release conhecidos.
  * `query-blacklist.txt.xz`: Lista de termos genéricos a desconsiderar nas buscas.
* `scripts/`
  * `m1.jar.xz`: Pacote de scripts Groovy padrão (`fn:amc`, `fn:sysinfo`, `fn:suball`, `fn:cleaner`, etc.) higienizado (sem telemetria, sem links de doação/Patreon e livre de travas de assinatura RSA).

---

## 🚀 Como Usar no FileBot

No arquivo `app.properties` do FileBot:

```properties
data.source.url = https://raw.githubusercontent.com/wbaamaral/filebot-data/main/data/
```

Ou aponte o script Groovy para carregar via URL do GitHub:
```bash
filebot -script https://raw.githubusercontent.com/wbaamaral/filebot-data/main/scripts/amc.groovy ...
```
