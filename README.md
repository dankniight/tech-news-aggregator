# Tech News Aggregator Site

This is a Python-based news aggregator that fetches articles from various tech news sources and displays them in a clean, modern web interface.

It is viewable here: https://dankniight.github.io/tech-news-aggregator/

## Features

- Aggregates news from multiple sources (The Verge, The Register, TechCrunch, Ars Technica, Futurism)
- Displays articles with images when available
- Responsive design that works on desktop and mobile
- Dark/light mode toggle with system preference detection
- Shuffle Mode for re-arranged non-chronological articles


## Architecture
```mermaid
graph TB
    %% News Sources
    A1[The Verge] --> B[Python News Aggregator]
    A2[The Register] --> B
    A3[TechCrunch] --> B
    A4[Ars Technica] --> B
    A5[Futurism] --> B
    
    %% Processing Pipeline
    subgraph "News Gathering Script (news_aggregator.py)"
        B --> C[RSS Feed Parsing]
        C --> D[Article Extraction]
        D --> E[Image Processing]
        E --> F[Data Formatting]
        F --> G[JSON Generation]
    end
    
    %% Static Files
    G --> H[articles.json]
    H --> I[GitHub Repository]
    
    %% GitHub Pages Deployment
    subgraph "GitHub Pages"
        I --> J[Public News Site]
        K[index.html] --> J
        L[CSS/JS Assets] --> J
    end
    
    
    %% User Interaction
    P[Users] --> J
    
    %% Automation
    T[Scheduled Updates] --> B
    
    %% Styling
    classDef sources fill:#FF6B35,stroke:#E55A2B,stroke-width:2px,color:#FFFFFF
    classDef processing fill:#2D3748,stroke:#4A5568,stroke-width:2px,color:#FFFFFF
    classDef storage fill:#805AD5,stroke:#6B46C1,stroke-width:2px,color:#FFFFFF
    classDef github fill:#24292E,stroke:#1B1F23,stroke-width:2px,color:#FFFFFF
    classDef frontend fill:#38A169,stroke:#2F855A,stroke-width:2px,color:#FFFFFF
    classDef users fill:#3182CE,stroke:#2C5282,stroke-width:2px,color:#FFFFFF
    
    class A1,A2,A3,A4,A5 sources
    class B,C,D,E,F,G processing
    class H storage
    class I,K,L github
    class J frontend
    class P,Q,R users
    class T processing
```

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the aggregator to fetch news:
   ```
   python src/news_aggregator.py
   ```

3. Serve the `index.html` file with any web server
