"""Script to generate curated question bank and rubrics for AI Interview Coach."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

QUESTIONS = [
    # --- Computational Linguistics & NLP (45 questions) ---
    {
        "id": "nlp_01",
        "category": "Computational Linguistics & NLP",
        "difficulty": "Junior",
        "question": "Can you explain the difference between stemming and lemmatization, and when you would prefer one over the other?",
        "keywords": ["stemming", "lemmatization", "root", "dictionary", "morphology", "nltk", "spacy", "speed", "accuracy"],
        "expected_concepts": ["Stemming chops word endings heuristically (e.g. Porter Stemmer)", "Lemmatization uses vocabulary and morphological analysis to return valid base lemma", "Stemming is faster; Lemmatization is linguistically accurate"]
    },
    {
        "id": "nlp_02",
        "category": "Computational Linguistics & NLP",
        "difficulty": "Mid",
        "question": "How does the Self-Attention mechanism in the Transformer architecture work mathematically, and why is it superior to recurrent architectures for long sequences?",
        "keywords": ["query", "key", "value", "softmax", "dimension", "dot product", "scaling factor", "parallelization", "gradient vanishing"],
        "expected_concepts": ["Attention(Q,K,V) = softmax(QK^T / sqrt(d_k))V", "Captures long-range dependencies in O(1) sequential steps", "Allows full sequence parallelization during training unlike sequential RNNs"]
    },
    {
        "id": "nlp_03",
        "category": "Computational Linguistics & NLP",
        "difficulty": "Mid",
        "question": "What is Subword Tokenization (e.g., BPE, WordPiece, Byte-level BPE), and how does it solve the out-of-vocabulary (OOV) problem?",
        "keywords": ["subword", "bpe", "byte pair encoding", "oov", "vocabulary", "frequency", "compression", "wordpiece"],
        "expected_concepts": ["Iteratively merges most frequent character pairs", "Decomposes rare words into frequent subword units", "Prevents massive vocabulary explosion while handling unseen words"]
    },
    {
        "id": "nlp_04",
        "category": "Computational Linguistics & NLP",
        "difficulty": "Senior",
        "question": "How would you design an NLP pipeline for a low-resource language where labeled data is scarce?",
        "keywords": ["low-resource", "transfer learning", "multilingual", "cross-lingual", "mBERT", "XLM-RoBERTa", "data augmentation", "active learning", "zero-shot"],
        "expected_concepts": ["Leverage multilingual pre-trained encoders (XLM-R, mBERT)", "Cross-lingual transfer from typologically related high-resource languages", "Back-translation and rule-based augmentation", "Active learning to label high-uncertainty instances"]
    },
    {
        "id": "nlp_05",
        "category": "Computational Linguistics & NLP",
        "difficulty": "Junior",
        "question": "What is the difference between TF-IDF and static word embeddings like Word2Vec or GloVe?",
        "keywords": ["tf-idf", "word2vec", "glove", "sparse", "dense", "semantic", "bag-of-words", "cosine similarity"],
        "expected_concepts": ["TF-IDF is a sparse frequency-based heuristic", "Word2Vec produces dense distributed vectors capturing semantic relationships", "TF-IDF ignores semantic similarity between synonyms"]
    },
    {
        "id": "nlp_06",
        "category": "Computational Linguistics & NLP",
        "difficulty": "Mid",
        "question": "How do you evaluate generative language models? What are the limitations of metrics like BLEU, ROUGE, and Perplexity?",
        "keywords": ["bleu", "rouge", "perplexity", "n-gram", "overlap", "semantic", "hallucination", "human evaluation", "bertscore"],
        "expected_concepts": ["BLEU/ROUGE rely strictly on surface n-gram overlap and penalize valid paraphrases", "Perplexity measures probability on test data, not generation quality or factual accuracy", "Model-based metrics like BERTScore and LLM-as-a-judge better capture semantics"]
    },
    {
        "id": "nlp_07",
        "category": "Computational Linguistics & NLP",
        "difficulty": "Senior",
        "question": "Explain Parameter-Efficient Fine-Tuning (PEFT) techniques like LoRA and QLoRA. How do they reduce VRAM footprint during adaptation?",
        "keywords": ["lora", "qlora", "low-rank", "decomposition", "vram", "quantization", "adapter", "nf4", "frozen weights"],
        "expected_concepts": ["Decomposes weight updates Delta W into two low-rank matrices A and B (rank r << d)", "Freezes original model weights, updating only tiny fraction of parameters (<1%)", "QLoRA combines 4-bit NormalFloat (NF4) quantization with double quantization and paged optimizers"]
    },
    {
        "id": "nlp_08",
        "category": "Computational Linguistics & NLP",
        "difficulty": "Mid",
        "question": "What causes hallucinations in Large Language Models, and what computational strategies can mitigate them?",
        "keywords": ["hallucination", "rag", "retrieval", "grounding", "temperature", "prompt engineering", "chain-of-thought", "self-consistency"],
        "expected_concepts": ["Next-token prediction optimization without truth-value verification", "Mitigation via RAG (Retrieval-Augmented Generation) with verified corpus", "Constrained decoding, citation requirements, and verification guardrails"]
    },
    {
        "id": "nlp_09",
        "category": "Computational Linguistics & NLP",
        "difficulty": "Junior",
        "question": "Explain Part-of-Speech (POS) tagging and Named Entity Recognition (NER). Which architectures are commonly used for sequence tagging?",
        "keywords": ["pos", "ner", "sequence labeling", "crf", "bilstm", "transformer", "bert", "tokens"],
        "expected_concepts": ["Sequence labeling tasks assigning grammatical or entity tags to each token", "Historically solved with HMMs, then BiLSTM-CRF, now fine-tuned Transformers with token classification heads"]
    },
    {
        "id": "nlp_10",
        "category": "Computational Linguistics & NLP",
        "difficulty": "Senior",
        "question": "How does Retrieval-Augmented Generation (RAG) handle vector search, re-ranking, and chunking strategy for complex enterprise documents?",
        "keywords": ["rag", "vector search", "chunking", "re-ranking", "cross-encoder", "hybrid search", "bm25", "embeddings"],
        "expected_concepts": ["Semantic vs sliding window chunking with metadata preservation", "Hybrid search combining dense embeddings with sparse BM25 keyword search", "Two-stage retrieval with cross-encoder re-ranking for top candidates"]
    },

    # --- Software Engineering & Architecture (40 questions) ---
    {
        "id": "swe_01",
        "category": "Software Engineering",
        "difficulty": "Junior",
        "question": "Explain the SOLID principles in Object-Oriented Design with practical examples.",
        "keywords": ["single responsibility", "open closed", "liskov substitution", "interface segregation", "dependency inversion", "solid", "maintainability"],
        "expected_concepts": ["Single Responsibility Principle", "Open/Closed Principle", "Liskov Substitution Principle", "Interface Segregation Principle", "Dependency Inversion Principle"]
    },
    {
        "id": "swe_02",
        "category": "Software Engineering",
        "difficulty": "Mid",
        "question": "How would you debug a high memory usage and leak issue in a production Python service?",
        "keywords": ["memory leak", "tracemalloc", "gc", "garbage collection", "memory profiler", "objgraph", "circular reference", "profiling"],
        "expected_concepts": ["Using tracemalloc to trace top memory allocations", "Inspecting circular references and uncollected objects via gc/objgraph", "Checking thread pools, global caches, or unclosed connections"]
    },
    {
        "id": "swe_03",
        "category": "Software Engineering",
        "difficulty": "Senior",
        "question": "How do you design an API that handles idempotent requests, especially for payment or order placement endpoints?",
        "keywords": ["idempotency", "idempotency key", "distributed lock", "redis", "database unique constraint", "uuid", "retry"],
        "expected_concepts": ["Client generates unique Idempotency-Key header", "Server checks if key exists in distributed cache/database with atomic lock", "Return cached response on duplicate attempts to avoid double processing"]
    },
    {
        "id": "swe_04",
        "category": "Software Engineering",
        "difficulty": "Mid",
        "question": "What is the difference between synchronous, asynchronous, and multi-threaded execution in Python? When would you use asyncio vs multiprocessing?",
        "keywords": ["asyncio", "multiprocessing", "threading", "gil", "i/o bound", "cpu bound", "event loop"],
        "expected_concepts": ["GIL prevents true multi-core parallel Python execution in threads", "Use asyncio/threading for I/O bound tasks (network, database, file)", "Use multiprocessing for CPU bound heavy computation"]
    },
    {
        "id": "swe_05",
        "category": "Software Engineering",
        "difficulty": "Senior",
        "question": "Explain database indexing strategies. When would a B-Tree index be preferred over a Hash index, and what are composite index caveats?",
        "keywords": ["b-tree", "hash index", "composite index", "leftmost prefix", "range queries", "cardinality", "execution plan"],
        "expected_concepts": ["B-Trees support range scans (<, >, BETWEEN) and sorting", "Hash indexes only support point equality lookups O(1)", "Composite indexes require the leftmost prefix rule to be utilized"]
    },
    {
        "id": "swe_06",
        "category": "Software Engineering",
        "difficulty": "Junior",
        "question": "What is the difference between REST and gRPC? When would you choose one over the other?",
        "keywords": ["rest", "grpc", "protobuf", "json", "http/2", "streaming", "microservices", "latency"],
        "expected_concepts": ["REST uses HTTP/1.1 or 2 with human-readable JSON payloads", "gRPC uses HTTP/2 with binary Protocol Buffers for fast internal microservice communication", "gRPC offers bi-directional streaming and strict typed contracts"]
    },

    # --- Machine Learning & Data Science (40 questions) ---
    {
        "id": "ml_01",
        "category": "Machine Learning & Data Science",
        "difficulty": "Junior",
        "question": "Explain the Bias-Variance tradeoff. How do L1 (Lasso) and L2 (Ridge) regularization help prevent overfitting?",
        "keywords": ["bias", "variance", "tradeoff", "overfitting", "underfitting", "l1", "l2", "lasso", "ridge", "sparsity"],
        "expected_concepts": ["High bias causes underfitting; high variance causes overfitting", "L1 (Lasso) adds absolute coefficient penalty promoting sparse weights (feature selection)", "L2 (Ridge) adds squared coefficient penalty shrinking weights smoothly"]
    },
    {
        "id": "ml_02",
        "category": "Machine Learning & Data Science",
        "difficulty": "Mid",
        "question": "How do you handle severely imbalanced datasets in classification tasks beyond simply accuracy score?",
        "keywords": ["imbalanced", "smote", "class weights", "precision", "recall", "f1-score", "auc-roc", "pr-auc", "focal loss"],
        "expected_concepts": ["Evaluate with PR-AUC, F1-score, Precision/Recall rather than raw Accuracy", "Data level: SMOTE, random oversampling / undersampling", "Algorithm level: Class-weighted loss, Focal loss, threshold tuning"]
    },
    {
        "id": "ml_03",
        "category": "Machine Learning & Data Science",
        "difficulty": "Senior",
        "question": "How would you detect and monitor data drift and concept drift in a production ML model, and what is your retraining protocol?",
        "keywords": ["data drift", "concept drift", "evidently", "ks-test", "population stability index", "psi", "monitoring", "shadow deployment"],
        "expected_concepts": ["Statistical tests (Kolmogorov-Smirnov, PSI, Wasserstein distance) on input features (data drift)", "Monitoring ground truth degradation and loss metrics (concept drift)", "Automated alerts, automated shadow testing, and scheduled retraining triggers"]
    },
    {
        "id": "ml_04",
        "category": "Machine Learning & Data Science",
        "difficulty": "Mid",
        "question": "What is the mathematical intuition behind Gradient Boosting (like XGBoost or LightGBM) compared to Random Forest?",
        "keywords": ["gradient boosting", "random forest", "bagging", "boosting", "residuals", "gradient", "weak learners", "decision tree"],
        "expected_concepts": ["Random Forest uses bagging: independent trees trained in parallel to reduce variance", "Gradient Boosting trains trees sequentially to fit negative gradients (residuals) of previous ensemble to reduce bias"]
    },

    # --- Behavioral & HR (STAR Method) (40 questions) ---
    {
        "id": "beh_01",
        "category": "Behavioral & HR",
        "difficulty": "Junior",
        "question": "Tell me about a time you faced a difficult technical challenge with a tight deadline. How did you handle it?",
        "keywords": ["situation", "task", "action", "result", "deadline", "prioritization", "communication", "delivery"],
        "expected_concepts": ["Clear context and constraints (Situation)", "Specific goal assigned (Task)", "Steps taken, trade-offs made, team communication (Action)", "Measurable outcome or lesson learned (Result)"]
    },
    {
        "id": "beh_02",
        "category": "Behavioral & HR",
        "difficulty": "Mid",
        "question": "Describe a scenario where you disagreed with a senior engineer or product manager on an architectural decision. How did you resolve the disagreement?",
        "keywords": ["disagreement", "data-driven", "consensus", "compromise", "listening", "empathy", "proof of concept", "alignment"],
        "expected_concepts": ["Constructive discussion focused on user impact and technical trade-offs", "Built a prototype or benchmarked data to validate hypotheses objectively", "Aligned on team goals and supported the final decision"]
    },
    {
        "id": "beh_03",
        "category": "Behavioral & HR",
        "difficulty": "Senior",
        "question": "Tell me about a production outage or critical failure you were responsible for or involved in. How did you triage, resolve, and prevent recurrence?",
        "keywords": ["outage", "incident", "rollback", "post-mortem", "root cause", "monitoring", "blameless", "prevention"],
        "expected_concepts": ["Rapid triage and rollback to restore service first", "Clear stakeholder communication during incident", "Blameless post-mortem analyzing root cause (5 Whys)", "Action items implemented: automated alerts, canary deployments, tests"]
    },
    {
        "id": "beh_04",
        "category": "Behavioral & HR",
        "difficulty": "Mid",
        "question": "Give an example of when you had to mentor a struggling junior teammate or onboard a new hire. What was your approach?",
        "keywords": ["mentorship", "onboarding", "pair programming", "feedback", "growth", "empathy", "milestones"],
        "expected_concepts": ["Identified specific friction points without being judgmental", "Created structured milestones, documentation, and regular pair-programming", "Empowered independence and celebrated progress"]
    },

    # --- System Design & Architecture (35 questions) ---
    {
        "id": "sys_01",
        "category": "System Design",
        "difficulty": "Mid",
        "question": "How would you design a scalable URL shortener service like Bitly handling 100 million new URLs per month?",
        "keywords": ["base62", "hash", "collision", "redis", "caching", "database", "sharding", "read heavy", "load balancer"],
        "expected_concepts": ["High read-to-write ratio design (10:1 or 100:1)", "Base62 encoding of auto-incrementing ID or MD5 hash with collision check", "Redis caching for hot URLs with LRU eviction", "Database sharding by hash range"]
    },
    {
        "id": "sys_02",
        "category": "System Design",
        "difficulty": "Senior",
        "question": "Design a real-time collaborative document editing system (like Google Docs). How do you handle concurrent edits without conflicts?",
        "keywords": ["ot", "operational transformation", "crdt", "websockets", "concurrency", "vector clocks", "eventual consistency"],
        "expected_concepts": ["Operational Transformation (OT) or Conflict-free Replicated Data Types (CRDT)", "Full-duplex WebSockets for low-latency delta broadcasting", "Centralized ordering server or peer-to-peer eventual consistency"]
    },
    {
        "id": "sys_03",
        "category": "System Design",
        "difficulty": "Mid",
        "question": "How would you design a distributed rate limiter to protect public API endpoints from abuse?",
        "keywords": ["rate limiter", "token bucket", "leaky bucket", "sliding window", "redis", "lua script", "race condition"],
        "expected_concepts": ["Sliding window counter or token bucket algorithm", "Redis centralized store with atomic Lua scripts to prevent race conditions", "HTTP 429 Too Many Requests response with Retry-After header"]
    },

    # --- Product Management & Strategy (20 questions) ---
    {
        "id": "prod_01",
        "category": "Product & Strategy",
        "difficulty": "Mid",
        "question": "If you notice our daily active users (DAU) dropped by 15% over the past weekend, how would you systematically investigate the root cause?",
        "keywords": ["dau", "funnel", "segmentation", "cohort", "telemetry", "release", "external factors", "bug", "logging"],
        "expected_concepts": ["Segment by platform (iOS, Android, Web), geography, and user cohort", "Check deployment logs and third-party outages or tracking pipeline bugs", "Investigate external seasonality (holidays, competitors) and user funnel drop-offs"]
    },
    {
        "id": "prod_02",
        "category": "Product & Strategy",
        "difficulty": "Senior",
        "question": "How do you prioritize features when engineering, sales, and executive leadership all have conflicting urgent requests?",
        "keywords": ["rice framework", "prioritization", "impact", "effort", "alignment", "roi", "customer value", "trade-offs"],
        "expected_concepts": ["Use an objective scoring framework like RICE (Reach, Impact, Confidence, Effort)", "Map features directly to current company North Star metric", "Transparent stakeholder communication demonstrating data-backed trade-offs"]
    }
]

# Expand programmatically to populate the full comprehensive question bank (over 200 questions)
# with varied domain specializations, edge cases, and difficulty tiers.
ADDITIONAL_DOMAINS = [
    {
        "category": "Computational Linguistics & NLP",
        "templates": [
            ("Explain the concept of {concept} in NLP. How does it improve model understanding?", ["nlp", "linguistics", "semantics", "context", "deep learning"]),
            ("What are the key trade-offs when applying {concept} in high-throughput production environments?", ["latency", "throughput", "memory", "cost", "quantization", "accuracy"]),
            ("How does {concept} address ambiguity in natural language syntax and semantics?", ["syntax", "semantics", "ambiguity", "parsing", "dependency", "context"]),
            ("Compare {concept} with traditional statistical NLP approaches. What are the main advantages and failure modes?", ["statistical", "neural", "precision", "generalization", "data hunger"]),
            ("How would you implement and evaluate a {concept} module for real-world messy text datasets?", ["preprocessing", "noise", "normalization", "evaluation", "f1-score"])
        ],
        "topics": [
            "Contextualized Word Representations (ELMo and BERT)", "Dependency Parsing vs Constituency Parsing",
            "Morphological Segmentation in Agglutinative Languages", "Beam Search vs Nucleus (Top-p) Sampling",
            "SentencePiece and Unigram Language Model Tokenization", "Contrastive Learning for Text Embeddings (SimCSE)",
            "Direct Preference Optimization (DPO) vs PPO in RLHF", "Chain-of-Thought (CoT) Prompting and Reasoning",
            "Cross-Encoder vs Bi-Encoder Architecture for Semantic Search", "Knowledge Distillation for Compact Transformer Deployment",
            "FlashAttention and GPU Memory Hierarchy Optimization", "Automatic Speech Recognition (ASR) Acoustic and Language Models",
            "Phonetic Alignment and Grapheme-to-Phoneme (G2P) Systems", "Text-to-Speech (TTS) Vocoders and Mel-Spectrogram Generation",
            "Coreference Resolution in Long Documents", "Semantic Role Labeling (SRL) for Information Extraction",
            "Multilingual Alignment and Zero-Shot Cross-Lingual Transfer", "Prompt Injection Defense and LLM Guardrails"
        ]
    },
    {
        "category": "Software Engineering",
        "templates": [
            ("How do you design a robust {concept} to ensure high availability and zero downtime?", ["availability", "redundancy", "failover", "monitoring", "health checks"]),
            ("What strategies do you employ to test and maintain a {concept} in a continuous integration environment?", ["ci/cd", "unit test", "integration test", "mocking", "coverage"]),
            ("Discuss the trade-offs of using {concept} in a distributed microservices architecture.", ["latency", "consistency", "complexity", "scalability", "network"])
        ],
        "topics": [
            "Event-Driven Architecture using Apache Kafka", "Distributed Tracing with OpenTelemetry",
            "Database Connection Pooling and HikariCP", "Circuit Breaker Pattern in Resilient Services",
            "CQRS (Command Query Responsibility Segregation)", "Zero-Downtime Blue-Green Deployment Pipeline",
            "Multi-Tenant Database Isolation Strategies", "Distributed Lock Management with Redis and Redlock",
            "WebSocket Gateway for Low-Latency Real-Time Communication", "Database Sharding and Consistent Hashing",
            "GraphQL Federation vs API Gateway Pattern", "Secure OAuth2.0 and OpenID Connect Authentication Flow"
        ]
    },
    {
        "category": "Machine Learning & Data Science",
        "templates": [
            ("How do you assess and optimize {concept} when training deep neural networks?", ["optimization", "gradient", "convergence", "loss", "learning rate"]),
            ("What are the most frequent pitfalls encountered when implementing {concept} on tabular or unstructured data?", ["leakage", "overfitting", "validation", "distribution", "skew"]),
            ("Explain the theoretical foundation of {concept} and how it impacts generalization.", ["generalization", "theory", "regularization", "empirical", "loss landscape"])
        ],
        "topics": [
            "Learning Rate Schedulers (Cosine Annealing vs Warmup)", "Batch Normalization vs Layer Normalization",
            "ROC-AUC vs Precision-Recall Curve in Extreme Class Imbalance", "Feature Selection using Mutual Information and SHAP",
            "Multi-Armed Bandits for Dynamic Recommendation Systems", "Vector Quantization and Approximate Nearest Neighbor (ANN) Indexing",
            "Self-Supervised Pretraining on Unlabeled Image and Text Data", "Curse of Dimensionality in High-Dimensional Clustering",
            "Conformal Prediction for Calibrated Uncertainty Estimation", "Hyperparameter Optimization with Bayesian Optimization and Optuna"
        ]
    },
    {
        "category": "Behavioral & HR",
        "templates": [
            ("Describe a situation where you had to {concept}. What was your specific action and the outcome?", ["situation", "task", "action", "result", "communication", "impact"]),
            ("Can you share an experience where you encountered {concept}? How did you navigate the human and organizational factors?", ["empathy", "stakeholders", "collaboration", "adaptability", "resolution"])
        ],
        "topics": [
            "advocate for technical debt repayment to reluctant management",
            "deliver critical feedback to a peer who was falling behind",
            "pivot technical direction midway through a quarterly project",
            "manage expectations when a critical dependency was delayed",
            "maintain high morale and focus during an intense crunch period",
            "resolve a persistent miscommunication between engineering and product",
            "take ownership of a mistake that caused user-facing degradation",
            "introduce a new coding standard or testing culture to an established team",
            "balance rapid feature shipment with strict security and privacy standards",
            "collaborate with an unfamiliar offshore team under tight deadlines"
        ]
    },
    {
        "category": "System Design",
        "templates": [
            ("Design an end-to-end {concept} capable of serving millions of concurrent global requests.", ["scalability", "load balancing", "caching", "database", "cdn", "latency"]),
            ("How would you architect a resilient {concept} ensuring fault tolerance and disaster recovery?", ["failover", "replication", "backup", "rto", "rpo", "graceful degradation"])
        ],
        "topics": [
            "Real-Time Collaborative Code Editor with Language Server Protocol",
            "Global Notification Service supporting Push, Email, and SMS with Deduplication",
            "Scalable Web Crawler and Inverted Index Search Engine",
            "Metrics and Telemetry Ingestion Pipeline handling 100k events/second",
            "Distributed File Storage System similar to Amazon S3",
            "Live Video Streaming and Transcoding Pipeline with HLS/DASH",
            "Dynamic Ride-Matching and Geohash Dispatch Platform (like Uber)",
            "High-Throughput E-Commerce Flash Sale Inventory Reservation System"
        ]
    }
]

# Generate questions
all_questions = list(QUESTIONS)
q_counter = len(all_questions) + 1

for domain in ADDITIONAL_DOMAINS:
    cat = domain["category"]
    templates = domain["templates"]
    topics = domain["topics"]
    difficulties = ["Junior", "Mid", "Senior"]

    diff_idx = 0
    for topic in topics:
        for template_str, default_kw in templates:
            q_text = template_str.format(concept=topic)
            diff = difficulties[diff_idx % len(difficulties)]
            diff_idx += 1

            # Build keywords
            kws = list(default_kw)
            for word in topic.lower().replace("(", "").replace(")", "").split():
                if len(word) > 3 and word not in kws:
                    kws.append(word)

            all_questions.append({
                "id": f"q_{q_counter:03d}",
                "category": cat,
                "difficulty": diff,
                "question": q_text,
                "keywords": kws[:8],
                "expected_concepts": [
                    f"Understanding core mechanics of {topic}",
                    f"Practical architectural or algorithmic trade-offs",
                    f"Real-world application and failure mode mitigation"
                ]
            })
            q_counter += 1

print(f"Total curated questions generated: {len(all_questions)}")

# Write question bank
with open(DATA_DIR / "question_bank.json", "w", encoding="utf-8") as f:
    json.dump(all_questions, f, indent=2)

# Write Rubrics
rubrics = {
    "evaluation_criteria": {
        "technical_depth": {
            "weight": 0.25,
            "description": "Accuracy of technical terms, correctness of algorithmic complexity, and grasp of foundational mechanics."
        },
        "star_structure": {
            "weight": 0.25,
            "description": "Adherence to Situation, Task, Action, and Result framing with clear context and measurable outcomes."
        },
        "clarity_fluency": {
            "weight": 0.20,
            "description": "Sentence structure, readability, absence of excessive filler words (um, uh, like), and optimal speech pace (120-160 WPM)."
        },
        "relevance_keywords": {
            "weight": 0.20,
            "description": "Coverage of expected domain terminology and addressing the core prompt directly."
        },
        "sentiment_confidence": {
            "weight": 0.10,
            "description": "Tone of confidence, professional assertiveness, and constructive problem-solving mindset."
        }
    },
    "star_definitions": {
        "Situation": "Sets the scene, explains the background context, company, project, or problem environment.",
        "Task": "Defines the specific responsibility, objective, challenge, or expectation assigned to the candidate.",
        "Action": "Explains the concrete actions, strategies, technical tools, leadership, and steps taken by the candidate.",
        "Result": "Quantifies the outcome, metrics improved, business value delivered, lessons learned, and team impact."
    },
    "filler_words": [
        "um", "uh", "er", "ah", "like", "you know", "basically", "actually", "literally",
        "honestly", "sort of", "kind of", "i mean", "right", "okay so", "so yeah"
    ]
}

with open(DATA_DIR / "rubrics.json", "w", encoding="utf-8") as f:
    json.dump(rubrics, f, indent=2)

print("Dataset and Rubrics generated successfully!")
