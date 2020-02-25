from django.core.serializers.json import Serializer as JSONSerializer

class Serializer(JSONSerializer):
    """
    This serializer supports an exclude_fields kwarg that will override the fields kwarg and instead return
    all the fields in the model excluding the given fields
    """
    def serialize(self, queryset, *, stream=None, exclude_fields=None, use_natural_foreign_keys=False,
                  use_natural_primary_keys=False, progress_output=None, object_count=0, **options):
        # Calculate all the fields available on the model that forms this queryset's outer model

        fields = []
        model_fields = None
        if isinstance(queryset, list):
            if len(queryset) > 0:
                model_fields = queryset[0]._meta.get_fields()
            else:
                # This is an empty queryset, nothing we can do except serialize to empty as well
                return super(Serializer, self).serialize(queryset,
                                                         stream=stream,
                                                         use_natural_foreign_keys=use_natural_foreign_keys,
                                                         use_natural_primary_keys=use_natural_primary_keys,
                                                         progress_output=progress_output,
                                                         object_count=object_count,
                                                         **options)
        else:
            model_fields = queryset.model._meta.get_fields()

        if exclude_fields:
            for field in model_fields:
                if hasattr(field, 'attname') and field.attname not in exclude_fields:
                    fields.append(field.attname)
        return super(Serializer, self).serialize(queryset,
                                                 stream=stream,
                                                 fields=fields,
                                                 use_natural_foreign_keys=use_natural_foreign_keys,
                                                 use_natural_primary_keys=use_natural_primary_keys,
                                                 progress_output=progress_output,
                                                 object_count=object_count,
                                                 **options)
