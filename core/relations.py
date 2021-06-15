from django.core.exceptions import ObjectDoesNotExist

from rest_framework.relations import PrimaryKeyRelatedField


class PrimaryKeyListRelatedField(PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            return [queryset.get(id=id) for id in data]
        except ObjectDoesNotExist:
            self.fail("does_not_exist", pk_value=data)
        except (TypeError, ValueError):
            self.fail("incorrect_type", data_type=type(data).__name__)
