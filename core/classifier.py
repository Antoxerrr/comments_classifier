import re

import joblib
import numpy as np
import polars as pl
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

from core.models import CommentData


def load_dataset(trusted_only: bool = False) -> pl.DataFrame:
    filters = {}
    if trusted_only:
        filters['is_trusted'] = True

    data = CommentData.objects.filter(**filters).values('text', 'is_toxic')
    return pl.DataFrame(list(data)).with_columns(
        pl.col('is_toxic').cast(pl.Float32)
    )


def preprocess_russian_text(text):
    text = text.lower()
    text = re.sub(r'[^а-яё\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def preprocess_data(data: pl.DataFrame) -> pl.DataFrame:
    return data.with_columns(pl.col('text').map_elements(preprocess_russian_text))


def predict_toxicity(text: str, vectorizer: TfidfVectorizer, model, threshold: float = 0.5):
    cleaned = preprocess_russian_text(text)
    vectorized = vectorizer.transform([cleaned])
    probability = model.predict_proba(vectorized)[0]

    toxic_prob = probability[1]
    prediction = 1 if toxic_prob > threshold else 0

    return prediction, toxic_prob


def save_model(model, vectorizer):
    joblib.dump(model, settings.BASE_DIR / 'models/toxic_classifier_model.pkl')
    joblib.dump(vectorizer, settings.BASE_DIR / 'models/toxic_vectorizer.pkl')


def train():
    df = load_dataset()
    df = preprocess_data(df)

    vectorizer = TfidfVectorizer(
        max_features=15000,
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.7,
        sublinear_tf=True
    )

    x = vectorizer.fit_transform(df['text'])
    y = df['is_toxic']

    x_train, x_test, y_train, y_test = train_test_split(
        x, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = LogisticRegression(
        C=1.0,
        class_weight='balanced',
        random_state=42,
        max_iter=1000,
    )

    print('Обучаем')
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    y_pred_proba = model.predict_proba(x_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.3f}")
    print("\nДетальный отчет:")
    print(classification_report(y_test, y_pred, target_names=['Нормальный', 'Токсичный']))
    print(f"F1-score (weighted): {f1_score(y_test, y_pred, average='weighted'):.3f}")
    print(f"F1-score для токсичных: {f1_score(y_test, y_pred, pos_label=1):.3f}")
    print(f"ROC-AUC: {roc_auc_score(y_test, y_pred_proba):.3f}")

    best_f1 = 0
    best_threshold = 0.5

    for threshold in [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]:
        y_pred_custom = (y_pred_proba > threshold).astype(int)
        f1 = f1_score(y_test, y_pred_custom, pos_label=1)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold

    print(f"Лучший порог: {best_threshold}, F1: {best_f1:.3f}")

    save_model(model, vectorizer)


if __name__ == '__main__':
    train()
