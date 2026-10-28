```mermaid
flowchart TD
    A[Start] --> B[Set base folder to script directory]
    B --> C[Define Qsub template with placeholders]
    C --> D[Detect elemental folders in base folder]
    D -->|No folders found| E[Print message and exit]
    D -->|Folders found| F[Loop over each elemental folder]

    F --> G[Recursively search for .d3 files containing band]
    G -->|No .d3 files found| H[Print message and skip folder]
    G -->|.d3 files found| I[Loop over each .d3 file]

    I --> J[Set element_band = .d3 filename without extension]
    J --> K[Search for corresponding .out file in same folder]
    K -->|.out file found| L[Set job_name_d12 = .out filename without extension]
    K -->|No .out file found| M[Set job_name_d12 = element_band]

    L --> N[Set qsub filename = element_band.qsub]
    M --> N

    N --> O[Check if qsub file already exists]
    O -->|Exists| P[Print message and skip]
    O -->|Does not exist| Q[Fill template placeholders: element_band & job_name_d12]
    Q --> R[Write content to qsub file]
    R --> S[Print confirmation]
    S --> I[Continue to next .d3 file]

    H --> F[Continue to next elemental folder]
    I --> F
    F --> T[End]