# Financial Intelligence Copilot

An evidence-first financial research application combining web research, document retrieval, and structured data analysis.

## Start

Copy `.env.example` to `.env` and fill in Tavily plus Azure OpenAI keys, then:

```bash
./start.sh
```

This starts the live API (`http://127.0.0.1:8000`) and the Vite frontend (`http://127.0.0.1:5173`). Open the frontend URL. Ctrl+C stops both.

```bash
./start.sh demo          # no API keys
./start.sh live-search   # Tavily only, extractive synthesis
```


```mermaid
flowchart TD
    U["用户：提出金融分析问题"] --> UI["React 界面"]
    UI --> API["FastAPI 应用"]

    API --> R["Research 模块<br/>"]
    API -.-> D["Document RAG 模块<br/>"]
    API -.-> S["Data / SQL 模块<br/>"]

    R --> WEB["外部网页、公告、新闻"]
    D -.-> DOC["上传的年报、PDF、内部文档"]
    S -.-> DB["数据库中的财务数据"]

    R --> OUT["答案、证据、数据来源"]
    D -.-> OUT
    S -.-> OUT
```
