"""
Train Custom NLP & ML Models for AI Interview Coach:
1. STAR Sentence Classifier (Situation, Task, Action, Result, General)
2. Question Domain & Category Classifier (NLP, SWE, ML, Behavioral, System Design, Product)
"""

import os
import pickle
import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

# -------------------------------------------------------------
# 1. STAR Sentence Classification Training Dataset
# -------------------------------------------------------------
STAR_DATASET = [
    # Situation sentences
    ("At my previous company, our payment processing microservice experienced high latency during flash sales.", "Situation"),
    ("During my tenure at DataFlow, our team was managing an unoptimized monolithic database.", "Situation"),
    ("In our university research lab, we were working with low-resource Indic languages that lacked annotated corpora.", "Situation"),
    ("When I joined the analytics team, the reporting pipeline took six hours every morning to run.", "Situation"),
    ("Our legacy web application was suffering from frequent memory leaks and random crashes in production.", "Situation"),
    ("Last year, our client required an urgent migration from on-premise servers to AWS within four weeks.", "Situation"),
    ("We noticed a 15% drop in daily active users immediately following our major v2.0 mobile release.", "Situation"),
    ("The company was experiencing severe communication bottlenecks between engineering and the product management team.", "Situation"),
    ("In 2023, our engineering department had no continuous integration or automated testing pipeline in place.", "Situation"),
    ("Our e-commerce checkout page was dropping 22% of shopping carts due to timeout errors.", "Situation"),
    ("We were tasked with launching a new recommendation engine right before Black Friday.", "Situation"),
    ("The existing NLP pipeline used static dictionary lookups which failed on modern internet slang.", "Situation"),
    ("Our team inherited a legacy Python codebase with zero documentation and massive technical debt.", "Situation"),
    ("At the startup, customer support tickets were skyrocketing due to unexpected sync errors.", "Situation"),
    ("We were facing severe GPU memory constraints when attempting to fine-tune 70B parameter models.", "Situation"),

    # Task sentences
    ("My goal was to reduce API response latency below 100 milliseconds without increasing infrastructure costs.", "Task"),
    ("I was assigned to lead the database sharding initiative and migrate millions of active records.", "Task"),
    ("My objective was to develop a cross-lingual transfer framework to enable zero-shot NER.", "Task"),
    ("I was responsible for diagnosing the root cause of the memory leaks and stabilizing the web service.", "Task"),
    ("The deliverable was to build an automated CI/CD pipeline and achieve at least 80% test coverage.", "Task"),
    ("I needed to reconcile conflicting requirements between the marketing director and our security leads.", "Task"),
    ("My mission was to design an idempotent payment gateway endpoint to prevent duplicate credit card charges.", "Task"),
    ("I was tasked with reducing our cloud infrastructure spend by 30% without sacrificing service availability.", "Task"),
    ("We had to ship the MVP within three sprints while maintaining strict GDPR compliance.", "Task"),
    ("My role was to mentor three junior developers and get them productive within their first month.", "Task"),
    ("I had to devise a scalable chunking and vector search strategy for 500,000 corporate PDF documents.", "Task"),
    ("The objective was to improve our model's F1 score on imbalanced minority classes above 0.85.", "Task"),
    ("I was asked to conduct a comprehensive blameless post-mortem after the severe production outage.", "Task"),

    # Action sentences
    ("I profiled the application memory using tracemalloc and pinpointed unclosed database connection pools.", "Action"),
    ("I implemented an asynchronous worker queue using Celery and Redis to decouple heavy email dispatches.", "Action"),
    ("I designed composite B-Tree indexes on the high-frequency lookup columns and refactored slow SQL joins.", "Action"),
    ("I organized daily 15-minute sync meetings and paired directly with the lead developer to review PRs.", "Action"),
    ("I utilized QLoRA 4-bit quantization and PEFT adapters to fine-tune the model on a single consumer GPU.", "Action"),
    ("I authored automated unit tests using pytest, mocked external APIs, and configured GitHub Actions workflows.", "Action"),
    ("I integrated a distributed rate limiter using the Token Bucket algorithm backed by atomic Redis Lua scripts.", "Action"),
    ("I organized a technical proof-of-concept demonstrating the latency difference between REST and gRPC.", "Action"),
    ("I implemented subword Byte Pair Encoding tokenization and trained custom embeddings with SentencePiece.", "Action"),
    ("I broke down the project into agile user stories, created JIRA milestones, and negotiated scope trade-offs.", "Action"),
    ("I deployed Prometheus metrics and Grafana dashboards to monitor p95 latency and memory usage in real time.", "Action"),
    ("I conducted one-on-one pair programming sessions each afternoon to help the junior engineer master Git rebase.", "Action"),
    ("I implemented a hybrid RAG retrieval pipeline combining dense vector embeddings with sparse BM25 search.", "Action"),
    ("I wrote a custom Python script to clean, deduplicate, and normalize the noisy web-scraped dataset.", "Action"),
    ("I set up blue-green deployments with Kubernetes and AWS Route 53 to allow instant zero-downtime rollbacks.", "Action"),

    # Result sentences
    ("As a result, API response times dropped by 64%, from 280ms down to 78ms.", "Result"),
    ("The database migration was completed two days ahead of schedule with zero customer-facing downtime.", "Result"),
    ("We achieved an 18.5% relative improvement in F1-score and published our findings at EMNLP.", "Result"),
    ("This eliminated the memory leak entirely, stabilizing uptime to 99.99% across the quarter.", "Result"),
    ("Our cloud hosting bill decreased by $12,000 per month, which earned our team an internal innovation award.", "Result"),
    ("Test coverage climbed from 14% to 89%, reducing post-release bug reports by 55%.", "Result"),
    ("The junior developers graduated into autonomous feature owners within six weeks, receiving glowing reviews.", "Result"),
    ("Checkout conversion rates rebounded by 24%, recovering approximately $180,000 in monthly revenue.", "Result"),
    ("The incident response time improved from 45 minutes to under 5 minutes thanks to automated alerting.", "Result"),
    ("The proof of concept persuaded the engineering committee to adopt gRPC, cutting payload sizes by 70%.", "Result"),
    ("Ultimately, our model achieved state-of-the-art accuracy on the benchmark with 8x faster inference speeds.", "Result"),
    ("The stakeholder alignment allowed us to launch the product on time, reaching 100,000 users in week one.", "Result"),

    # General / Conversational sentences
    ("That is a fantastic question and one I have thought about extensively throughout my career.", "General"),
    ("In general, I believe communication and continuous testing are foundational to software craftsmanship.", "General"),
    ("Let me begin by providing a bit of context regarding how our team was structured.", "General"),
    ("I always strive to balance rapid iteration with long-term software maintainability.", "General"),
    ("To summarize, that experience taught me the paramount importance of measuring before optimizing.", "General"),
    ("Yes, I would be delighted to elaborate further on any specific part of that implementation.", "General"),
    ("Thank you for asking; this was definitely one of the most rewarding milestones of my engineering journey.", "General"),
    ("I consider myself an empathetic teammate who listens first before proposing architectural changes.", "General")
]


def train_star_classifier():
    print("=" * 60)
    print("Training STAR Framework Sentence Classifier...")
    print("=" * 60)

    texts = [item[0] for item in STAR_DATASET]
    labels = [item[1] for item in STAR_DATASET]

    # Pipeline with TF-IDF and Logistic Regression
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 3),
            min_df=1,
            sublinear_tf=True,
            lowercase=True
        )),
        ('clf', LogisticRegression(
            C=5.0,
            max_iter=500,
            class_weight='balanced',
            random_state=42
        ))
    ])

    pipeline.fit(texts, labels)

    # Cross validation evaluation
    cv_scores = cross_val_score(pipeline, texts, labels, cv=3)
    print(f"STAR Classifier 3-Fold Cross-Validation Accuracy: {cv_scores.mean() * 100:.2f}% (+/- {cv_scores.std() * 100:.2f}%)")

    preds = pipeline.predict(texts)
    print("\nTraining Classification Report:")
    print(classification_report(labels, preds))

    model_path = BASE_DIR / "star_classifier.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"[OK] Saved STAR Classifier model to {model_path}")
    return pipeline


def train_question_domain_classifier():
    print("\n" + "=" * 60)
    print("Training Question Domain & Category Classifier...")
    print("=" * 60)

    # Load question bank
    with open(DATA_DIR / "question_bank.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    texts = [q["question"] for q in questions]
    categories = [q["category"] for q in questions]

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True,
            lowercase=True
        )),
        ('clf', LogisticRegression(
            C=3.0,
            max_iter=500,
            class_weight='balanced',
            random_state=42
        ))
    ])

    X_train, X_test, y_train, y_test = train_test_split(texts, categories, test_size=0.2, random_state=42, stratify=categories)
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Question Category Classifier Test Accuracy: {acc * 100:.2f}%")
    print("\nTest Classification Report:")
    print(classification_report(y_test, preds, zero_division=0))

    # Refit on full dataset for maximum generalization in production
    pipeline.fit(texts, categories)

    model_path = BASE_DIR / "question_classifier.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"[OK] Saved Question Category Classifier to {model_path}")
    return pipeline


if __name__ == "__main__":
    train_star_classifier()
    train_question_domain_classifier()
    print("\nAll ML models successfully trained and serialized!")
