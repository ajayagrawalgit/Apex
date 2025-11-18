# Apex Data Flow Diagram

## System Architecture Flow

```mermaid
flowchart TD
    Start([User Input: URL]) --> RootAgent[Root Agent<br/>Gemini 2.5 Flash<br/>Orchestrator]
    
    RootAgent --> Scrape[Scrape Website Tool]
    Scrape --> CloudScraper[Cloudscraper<br/>Bypass Cloudflare]
    
    CloudScraper -->|Success| ScrapedData{Scraped Data<br/>Status: Success?}
    CloudScraper -->|Connection Error| DomainError[Domain Resolution Failed]
    CloudScraper -->|Cloudflare Challenge| CloudflareError[Cloudflare Protection]
    CloudScraper -->|Other Error| GenericError[Generic Error]
    
    DomainError --> ErrorResult[Error Result:<br/>status: error<br/>error: Domain resolution failed]
    CloudflareError --> ErrorResult
    GenericError --> ErrorResult
    
    ScrapedData -->|Yes| Content[Website Content<br/>Max 5000 chars]
    ScrapedData -->|No| ErrorResult
    
    Content --> Analyze[Analyze Agent Tool]
    
    Analyze --> PatternMatch[Pattern Matching Engine]
    PatternMatch --> BadPatterns[Check BAD_PATTERNS:<br/>seed phrase, private key,<br/>airdrop, free crypto, etc.]
    PatternMatch --> URLFlags[Check URL_RED_FLAGS:<br/>Suspicious TLDs, punycode]
    PatternMatch --> HTTPStatus[Check HTTP Status<br/>& Domain Resolution]
    
    BadPatterns --> Scoring[Scoring Algorithm]
    URLFlags --> Scoring
    HTTPStatus --> Scoring
    
    Scoring --> Verdict{Calculate Verdict:<br/>Score >= 4: Malicious<br/>Score >= 2: Suspicious<br/>Else: Benign}
    
    Verdict -->|Unsafe = 1| AnalysisResult[Analysis Result:<br/>unsafe: 1<br/>verdict: malicious/suspicious<br/>reasons: [...]<br/>insights: [...]]
    Verdict -->|Unsafe = 0| DeepCheck{Trigger Deep Check?}
    
    DeepCheck -->|Yes| DeepCheckTool[Deep Check Agent Tool]
    DeepCheck -->|No| AnalysisResult
    
    DeepCheckTool --> FormAnalysis[Form Field Analysis:<br/>Check for seed/mnemonic inputs]
    DeepCheckTool --> JSObfuscation[JS Obfuscation Detection:<br/>atob, eval, fromCharCode]
    DeepCheckTool --> DataExfil[Data Exfiltration Detection:<br/>fetch, xhr, sendbeacon]
    DeepCheckTool --> BrandMismatch[Brand Mismatch Detection:<br/>Compare domain vs content brands]
    DeepCheckTool --> TLDCheck[Suspicious TLD Link Analysis]
    
    FormAnalysis --> DeepResult[Deep Check Result:<br/>unsafe: 0|1<br/>ai_opinion: str<br/>reasons: [...]<br/>insights: [...]]
    JSObfuscation --> DeepResult
    DataExfil --> DeepResult
    BrandMismatch --> DeepResult
    TLDCheck --> DeepResult
    
    AnalysisResult --> Synthesis[AI Synthesis<br/>Root Agent Combines Results]
    DeepResult --> Synthesis
    ErrorResult --> Synthesis
    
    Synthesis --> HumanReadable[Generate Human-Readable Summary]
    HumanReadable --> Output([Output to User:<br/>Safety Verdict<br/>Reasons & Insights<br/>Actionable Recommendations])
    
    style RootAgent fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    style Scrape fill:#4ecdc4,stroke:#2d9cdb,stroke-width:2px
    style Analyze fill:#95e1d3,stroke:#2d9cdb,stroke-width:2px
    style DeepCheckTool fill:#f38181,stroke:#c92a2a,stroke-width:2px
    style Synthesis fill:#a8e6cf,stroke:#2d9cdb,stroke-width:2px
    style Output fill:#ffd93d,stroke:#f6c23e,stroke-width:3px
```

## Detailed Component Flow

```mermaid
sequenceDiagram
    participant User
    participant RootAgent as Root Agent<br/>(Orchestrator)
    participant Scraper as Scraper Agent
    participant Analyzer as Analyzer Agent
    participant DeepCheck as Deep Check Agent
    participant AI as Gemini AI<br/>(Synthesis)

    User->>RootAgent: Submit URL for analysis
    RootAgent->>Scraper: scrape_website(url)
    Scraper->>Scraper: Fetch content via Cloudscraper
    Scraper->>Scraper: Handle errors (DNS, Cloudflare, etc.)
    Scraper-->>RootAgent: Return scraped_data
    
    RootAgent->>Analyzer: analyze_agent(scraped_data, url)
    Analyzer->>Analyzer: Pattern matching (BAD_PATTERNS)
    Analyzer->>Analyzer: URL analysis (RED_FLAGS)
    Analyzer->>Analyzer: Calculate score & verdict
    Analyzer-->>RootAgent: Return analysis_result
    
    alt analysis_result.unsafe == 0
        RootAgent->>DeepCheck: deep_check_agent(scraped_data, url, analysis_result)
        DeepCheck->>DeepCheck: Form field analysis
        DeepCheck->>DeepCheck: JS obfuscation detection
        DeepCheck->>DeepCheck: Data exfiltration check
        DeepCheck->>DeepCheck: Brand mismatch detection
        DeepCheck->>DeepCheck: TLD link analysis
        DeepCheck-->>RootAgent: Return deep_check_result
    end
    
    RootAgent->>AI: Synthesize all findings
    AI->>AI: Generate human-readable summary
    AI-->>RootAgent: Return formatted response
    RootAgent-->>User: Display safety verdict & insights
```

## Decision Points Flow

```mermaid
flowchart LR
    A[URL Input] --> B{Scrape Success?}
    B -->|Yes| C[Content Retrieved]
    B -->|No| D[Domain Resolution Failed]
    D --> E[Mark as UNSAFE]
    
    C --> F[Initial Analysis]
    F --> G{Unsafe Flag?}
    G -->|1 Unsafe| H[Return UNSAFE Verdict]
    G -->|0 Safe| I[Deep Check Required]
    
    I --> J[Advanced Analysis]
    J --> K{Deep Check<br/>Found Issues?}
    K -->|Yes| L[Mark as UNSAFE]
    K -->|No| M[Mark as SAFE]
    
    H --> N[AI Synthesis]
    L --> N
    M --> N
    E --> N
    
    N --> O[Human-Readable Output]
    O --> P[User Receives Result]
    
    style E fill:#ff6b6b,color:#fff
    style H fill:#ff6b6b,color:#fff
    style L fill:#ff6b6b,color:#fff
    style M fill:#51cf66,color:#fff
    style N fill:#ffd93d
    style P fill:#4ecdc4,color:#fff
```

## Data Transformation Flow

```mermaid
flowchart TD
    URL[Raw URL String] --> Scrape
    
    Scrape --> ScrapedData["Scraped Data:<br/>{<br/>  status: 'success'|'error',<br/>  status_code: int,<br/>  content: str (5000 chars max),<br/>  error: str (if error)<br/>}"]
    
    ScrapedData --> Analysis
    
    Analysis --> AnalysisData["Analysis Result:<br/>{<br/>  unsafe: 0|1,<br/>  verdict: 'benign'|'suspicious'|'malicious',<br/>  reasons: [str],<br/>  insights: [str],<br/>  indicators: {<br/>    status, status_code,<br/>    content_length,<br/>    num_digits_in_url,<br/>    has_punycode<br/>  }<br/>}"]
    
    AnalysisData -->|if unsafe == 0| DeepCheck
    
    DeepCheck --> DeepCheckData["Deep Check Result:<br/>{<br/>  unsafe: 0|1,<br/>  ai_opinion: str,<br/>  reasons: [str],<br/>  insights: [str]<br/>}"]
    
    AnalysisData --> Synthesis
    DeepCheckData --> Synthesis
    
    Synthesis --> FinalOutput["Final Output:<br/>Human-Readable Summary:<br/>- URL analyzed<br/>- Safety verdict (SAFE/UNSAFE)<br/>- Detailed reasons<br/>- Actionable insights<br/>- Recommendations"]
    
    style URL fill:#e9ecef
    style ScrapedData fill:#cfe2ff
    style AnalysisData fill:#d1e7dd
    style DeepCheckData fill:#fff3cd
    style FinalOutput fill:#d4edda,stroke:#28a745,stroke-width:3px
```

## Error Handling Flow

```mermaid
flowchart TD
    Start[URL Input] --> TryScrape[Attempt Scrape]
    
    TryScrape -->|Success| Success[Content Retrieved]
    TryScrape -->|ConnectionError| DNSFail[Domain Resolution Failed]
    TryScrape -->|CloudflareChallenge| CloudflareBlock[Cloudflare Protection]
    TryScrape -->|Timeout| TimeoutError[Request Timeout]
    TryScrape -->|HTTP Error| HTTPError[HTTP Status >= 400]
    TryScrape -->|Other Exception| GenericError[Generic Error]
    
    DNSFail --> ErrorAnalysis[Analyze Error Type]
    CloudflareBlock --> ErrorAnalysis
    TimeoutError --> ErrorAnalysis
    HTTPError --> ErrorAnalysis
    GenericError --> ErrorAnalysis
    
    ErrorAnalysis --> ErrorResult["Error Result:<br/>status: 'error'<br/>error: 'Domain resolution failed.'<br/>or specific error message"]
    
    ErrorResult --> MarkUnsafe[Mark as UNSAFE<br/>Add to reasons]
    Success --> NormalFlow[Normal Analysis Flow]
    
    MarkUnsafe --> Synthesis
    NormalFlow --> Synthesis
    
    Synthesis --> Output[Return Error Explanation<br/>to User]
    
    style DNSFail fill:#ff6b6b,color:#fff
    style CloudflareBlock fill:#ff8787,color:#fff
    style TimeoutError fill:#ffa94d,color:#fff
    style HTTPError fill:#ffd43b
    style GenericError fill:#ffc9c9
    style ErrorResult fill:#ffe3e3,stroke:#c92a2a,stroke-width:2px
    style MarkUnsafe fill:#ff6b6b,color:#fff,stroke-width:3px
```

---

## Legend

- **Blue boxes**: Data processing components
- **Red boxes**: Error states or unsafe verdicts
- **Green boxes**: Safe verdicts or successful operations
- **Yellow boxes**: AI synthesis and final output
- **Diamond shapes**: Decision points
- **Rounded rectangles**: Start/End points

