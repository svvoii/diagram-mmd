# Choosing a diagram type

Default: **`flowchart TD`** for system architecture, code logic, and data flow.

| You want to show... | Use | First line |
|---|---|---|
| System architecture / components & data flow | flowchart with subgraphs | `flowchart TD` |
| Left-to-right pipeline / CI flow | flowchart LR | `flowchart LR` |
| Interactions between actors over time | sequence diagram | `sequenceDiagram` |
| Code structure: classes, modules, interfaces | class diagram | `classDiagram` |
| Database schema / entities & relations | ER diagram | `erDiagram` |
| State machines, lifecycles | state diagram | `stateDiagram-v2` |
| Project plan / milestones | gantt | `gantt` |
| Proportions / shares | pie | `pie` |
| Roadmap on a timeline | timeline | `timeline` |
| 2x2 prioritization | quadrant chart | `quadrantChart` |
| User journey steps & satisfaction | journey | `journey` |
| Git branch history | git graph | `gitGraph` |
| Concept map | mindmap | `mindmap` |
| Host / network topology (Mermaid ≥ v11.3) | architecture | `architecture-beta` |
| UI layout blocks | block | `block-beta` |
| Packet / protocol fields | packet | `packet-beta` |
| Flow magnitudes (in → out) | sankey | `sankey-beta` |
| Numeric series | xy chart | `xyChart` |
| C4 model (context / container / component) | C4 | `C4Context` |
| Requirements traceability | requirement | `requirementDiagram` |

## Minimal examples (copy-paste starters)

### flowchart (default — architecture & logic)
```mermaid
flowchart TD
    subgraph CLIENT["Client"]
        UI["Web UI"]
    end
    subgraph SERVER["Server"]
        API["REST API"] --> SVC["Service"]
    end
    DB[("Database")]
    UI -- HTTP --> API
    SVC --> DB
```

### sequenceDiagram (interactions over time)
```mermaid
sequenceDiagram
    actor U as User
    participant A as API
    participant D as DB
    U->>A: GET /items
    A->>D: SELECT * FROM items
    D-->>A: rows
    A-->>U: 200 JSON
```

### classDiagram (code structure)
```mermaid
classDiagram
    class HybridRetriever {
        +retrieve(query, top_k) list
        -_vector_search(query, k)
        -_bm25_search(query, k)
    }
    class Reranker {
        +rerank(query, chunks, top_k)
    }
    HybridRetriever ..> Reranker : uses
```

### erDiagram (database schema)
```mermaid
erDiagram
    DOCUMENT ||--o{ CHUNK : has
    DOCUMENT {
        string id
        string source
        string format
    }
    CHUNK {
        string id
        string document_id
        int chunk_index
        string text
    }
```

### stateDiagram-v2 (lifecycles)
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Retrieving : question
    Retrieving --> Generating : chunks
    Generating --> Idle : answer
    Retrieving --> Idle : no results
```

### gantt (plans)
```mermaid
gantt
    title Release plan
    dateFormat YYYY-MM-DD
    section Ingestion
    Docling parser   :a1, 2026-01-05, 5d
    section Query
    Reranker         :a2, after a1, 3d
```

### pie (shares)
```mermaid
pie title Chunk sources
    "PDF" : 45
    "DOCX" : 30
    "Images" : 25
```

### gitGraph (branch history)
```mermaid
gitGraph
    commit
    branch feature
    checkout feature
    commit
    checkout main
    merge feature
```

### mindmap (concepts)
```mermaid
mindmap
  root((RAG system))
    Ingestion
      Docling
      Chunking
    Retrieval
      BM25
      Vector
      RRF
    Generation
      Providers
      Prompt
```

### architecture-beta (host topology, Mermaid ≥ v11.3)
```mermaid
architecture-beta
    group host(cloud)[Server]
    service api(server)[API] in host
    service db(database)[ChromaDB] in host
    api:R --> L:db
```

For the remaining types (`timeline`, `quadrantChart`, `journey`, `block-beta`, `packet-beta`, `sankey-beta`, `xyChart`, `C4*`, `requirementDiagram`) see the official docs at https://mermaid.js.org — the first-line keyword above is all you need to start.
