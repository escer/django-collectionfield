# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import decimal

from django.db import models

from collectionfield.models import CollectionField
from collectionfield.validators import (
    ItemMinValueValidator, ItemMaxValueValidator
)


class StringListModel(models.Model):

    values = CollectionField()


class ChoiceStringListModel(models.Model):

    values = CollectionField(
        choices=(
            ('aaa', "AAA"),
            ('bbb', "BBB"),
            ('ccc', "CCC"),
            ('ddd', "DDD"),
        )
    )


class SortedUniqueStringListModel(models.Model):

    values = CollectionField(sort=True, unique_items=True)


def default_string_list():
    return ['Default', 'Values']


class DefaultStringListModel(models.Model):

    values = CollectionField(blank=True, default=default_string_list)


class OptionalRangedIntegerListModel(models.Model):

    values = CollectionField(
        item_type=int,
        validators=[ItemMinValueValidator(1), ItemMaxValueValidator(5)],
        blank=True
    )


class DecimalSetModel(models.Model):

    values = CollectionField(item_type=decimal.Decimal, collection_type=set)


def default_decimal_set():
    return {decimal.Decimal('0.0')}


class DefaultDecimalSetModel(models.Model):

    values = CollectionField(
        item_type=decimal.Decimal, collection_type=set,
        blank=True, default=default_decimal_set
    )


class SortedDecimalListModel(models.Model):

    values = CollectionField(item_type=decimal.Decimal, sort=True)


class IntegerTupleModel(models.Model):

    values = CollectionField(item_type=int, collection_type=tuple)


class DefaultIntegerTupleModel(models.Model):

    values = CollectionField(
        item_type=int, collection_type=tuple, blank=True, default=(-1,)
    )


class OptionalIntegerTupleModel(models.Model):

    values = CollectionField(
        item_type=int, collection_type=tuple, blank=True
    )


class OptionalGroupedChoiceStringListModel(models.Model):

    values = CollectionField(
        blank=True,
        choices=(
            (
                'Group A',
                (
                    ('a1', "A1"),
                    ('a2', "A2"),
                )
            ),
            (
                'Group B',
                (
                    ('b1', "B1"),
                    ('b2', "B2"),
                )
            )
        )
    )


class OptionalGroupedChoiceIntegerListModel(models.Model):

    values = CollectionField(
        item_type=int, blank=True,
        choices=(
            (
                'Group 1',
                (
                    (11, "1-1"),
                    (12, "1-2"),
                )
            ),
            (
                'Group 2',
                (
                    (21, "2-1"),
                    (22, "2-2"),
                )
            )
        )
    )


class Max10CharsStringListModel(models.Model):

    values = CollectionField(max_length=10)


class Max5ItemsStringListModel(models.Model):

    values = CollectionField(max_items=5)


class MultipleFieldsModel(models.Model):
    
    values = CollectionField(
        choices=(
            ('aaa', "AAA"),
            ('bbb', "BBB"),
            ('ccc', "CCC"),
            ('ddd', "DDD"),
        )
    )
    name = models.CharField(max_length=20)
    active = models.BooleanField(default=True)

