# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import django
from django.db.models.lookups import Contains


class Has(Contains):

    lookup_name = 'has'

    def __init__(self, lhs, rhs):
        super(Has, self).__init__(lhs, rhs)
        if not self.rhs_is_direct_value():
            raise NotImplementedError(
                'Lookup "{0}" supports only direct values'.format(
                    self.lookup_name
                )
            )

    def get_prep_lookup(self):
        if django.VERSION >= (1, 10):
            if hasattr(self.rhs, '_prepare'):
                value = self.rhs._prepare(self.lhs.output_field)
            else:
                value = self.rhs
            value = self.lhs.output_field.get_prep_value([value])
        else:
            value = self.lhs.output_field.get_prep_lookup(
                self.lookup_name, [self.rhs]
            )
        return value

    def get_rhs_op(self, connection, rhs):
        return connection.operators['contains'] % rhs


class HasMany(Has):
    lookup_name = None  # base class
    join_conditions_with = None

    def __init__(self, lhs, rhs):
        super(HasMany, self).__init__(lhs, rhs)
        self.rhs_items = list(rhs)

    def get_prep_lookup(self):
        if django.VERSION >= (1, 10):
            if hasattr(self.rhs, '_prepare'):
                value = self.rhs._prepare(self.lhs.output_field)
            else:
                value = self.rhs
            value = self.lhs.output_field.get_prep_value(value)
        else:
            value = self.lhs.output_field.get_prep_lookup(
                self.lookup_name, self.rhs
            )
        return value

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        sql_items, params = [], []
        for rhs_item in self.rhs_items:
            rhs, rhs_params = \
                Has(self.lhs, rhs_item).process_rhs(compiler, connection)
            rhs = self.get_rhs_op(connection, rhs)
            sql_items.append('%s %s' % (lhs, rhs))
            params.extend(lhs_params + rhs_params)
        return self.join_conditions_with.join(sql_items), params

    def get_rhs_op(self, connection, rhs):
        return connection.operators['contains'] % rhs


class HasAll(HasMany):
    lookup_name = 'hasall'
    join_conditions_with = ' AND '


class HasAny(HasMany):
    lookup_name = 'hasany'
    join_conditions_with = ' OR '
