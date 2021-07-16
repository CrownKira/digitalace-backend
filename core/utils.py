from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


def validate_reference_uniqueness(serializer, model, reference, id):
    # TODO: handle no both pk=id and serializer.instance.id
    company = serializer.context["request"].user.company

    if serializer.context["request"].method in ["POST"]:
        if model.objects.filter(company=company, reference=reference).exists():
            msg = _(
                f"A/an {model._meta.model_name} with this reference already exists"
            )
            raise serializers.ValidationError(msg)
    elif (
        model.objects.exclude(pk=id or serializer.instance.id)
        .filter(company=company, reference=reference)
        .exists()
    ):
        msg = _(
            f"A/an {model._meta.model_name} with this reference already exists"
        )
        raise serializers.ValidationError(msg)


def all_unique(x):
    seen = set()
    return not any(i in seen or seen.add(i) for i in x)


def validate_reference_uniqueness_in_data(data):
    if isinstance(data, list) and not all_unique(
        [item.get("reference") for item in data]
    ):
        msg = _("Duplicate reference not allowed")
        raise serializers.ValidationError(msg)
    return data
