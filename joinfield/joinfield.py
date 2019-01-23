from django.db import router
from django.db.models import ForeignKey
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor


class JoinFieldDescriptor(ForwardManyToOneDescriptor):
    def __set__(self, instance, value):
        """
        Set the related instance or literal value through the forward relation.

        when setting ``child.parent = parent``:

        - ``self`` is the descriptor managing the ``parent`` attribute
        - ``instance`` is the ``child`` instance
        - ``value`` is the ``parent`` instance on the right of the equal sign
           or a literal value
        """
        if isinstance(value, self.field.remote_field.model._meta.concrete_model):
            # Make sure the router allows the relation
            if instance._state.db is None:
                instance._state.db = router.db_for_write(instance.__class__, instance=value)
            elif value._state.db is None:
                value._state.db = router.db_for_write(value.__class__, instance=instance)
            elif value._state.db is not None and instance._state.db is not None:
                if not router.allow_relation(value, instance):
                    raise ValueError('Cannot assign "%r": the current database router prevents this relation.' % value)

            # If value is a related instance, get the value from the related
            # field attribute
            for lh_field, rh_field in self.field.related_fields:
                setattr(instance, lh_field.attname, getattr(value, self.field.target_field.name))

            # Set the related instance cache used by __get__ to avoid an SQL query
            # when accessing the attribute we just set.
            if hasattr(self.field, 'set_cached_value'):
                # Django >= 2.0
                self.field.set_cached_value(instance, value)
            else:
                # Django <= 1.11
                setattr(instance, self.cache_name, value)

        else:
            if hasattr(self.field, 'set_cached_value'):
                # Django >= 2.0
                self.field.set_cached_value(instance, None)
            else:
                # Django <= 1.11
                setattr(instance, self.cache_name, None)

            # Set the values of the related field.
            for lh_field, rh_field in self.field.related_fields:
                setattr(instance, lh_field.attname, value)

    def __get__(self, instance, cls=None):
        try:
            return super(JoinFieldDescriptor, self).__get__(instance, cls=cls)
        except self.field.related_model.DoesNotExist:
            return None


class JoinField(ForeignKey):
    forward_related_accessor_class = JoinFieldDescriptor
    requires_unique_target = False

    def __init__(self, *args, **kwargs):
        kwargs['db_constraint'] = kwargs.get('db_constraint', False)
        self.db_field_name = kwargs.pop('db_field_name', None)
        super(JoinField, self).__init__(*args, **kwargs)

    def get_attname(self):
        return self.db_field_name or super(JoinField, self).get_attname()
