import polars as pl

from core.classifier import load_dataset, train
from core.models import CommentData


def run():
    train()
