from __future__ import annotations

from abc import ABC
from math import prod
from typing import List, Iterable

from title.matchers import Matcher, RegexpMatcher, TitleMatcher
from common.torrent import Torrent


class Builder(ABC):
    _matchers: List[Matcher]
    _name: str

    def _extend(self, matcher: Iterable[Matcher]) -> None:
        self._matchers.extend(matcher)

    def get(self) -> Iterable[Matcher]:
        return self._matchers


class ChanceRatioVectorBuilder(Builder):
    _weights: dict[str, float]

    def __init__(self, weights: dict[str, float]):
        self._matchers = []
        self._weights = weights
        self._patterns = []

    def add_words(self, meta_name: str, percent: int, word_patterns: Iterable[str]) -> ChanceRatioVectorBuilder:
        total_weights = sum([x for k, x in self._weights.items()])
        all = [
            RegexpMatcher(type, rf"\b{word}\b", (weight / total_weights) * percent / 100, meta_name)
            for word in word_patterns
            for type, weight
            in self._weights.items()
        ]
        self._extend(all)
        return self

def for_media(*types: str):
    return ChanceRatioVectorBuilder({t: 1 for t in types})


def for_media_refine(type_fractions: dict[str, float]) -> ChanceRatioVectorBuilder:
    return ChanceRatioVectorBuilder(type_fractions)


def make_title_matcher(*builders: Builder):
    all = [m for b in builders for m in b.get()]
    return TitleMatcher(*all)
