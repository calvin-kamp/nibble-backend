from django.utils import timezone
from rest_framework import serializers

from accounts.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        exclude = (
            "data_consent_date_granted",
            "data_consent_date_revoked",
            "data_consent_version",
        )
        extra_kwargs = {
            "date_of_birth": {
                "write_only": True,
            }
        }

    def get_age(self, obj):
        if obj.date_of_birth is None:
            return None

        today = timezone.now().date()
        date_of_birth = obj.date_of_birth

        return (
            today.year
            - date_of_birth.year
            - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        )

    def validate_username(self, value):
        queryset = Profile.objects.filter(username=value)

        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("Benutzername bereits in Nutzung.")

        return value

    def validate(self, attrs):
        data_consent = attrs.get("data_consent", self.instance.data_consent)

        if data_consent is False:
            attrs["sex"] = None
            attrs["height"] = None
            attrs["weight"] = None
            attrs["target_calories"] = None
            attrs["target_fat"] = None
            attrs["target_protein"] = None
            attrs["target_carbs"] = None
            attrs["goal"] = None
            attrs["date_of_birth"] = None

        if (
            self.instance.data_consent_date_granted is not None
            and data_consent is False
        ):
            attrs["data_consent_date_revoked"] = timezone.now()

        if data_consent is True and self.instance.data_consent is False:
            attrs["data_consent_date_granted"] = timezone.now()

        if data_consent is False and self.instance.data_consent is True:
            attrs["data_consent_date_revoked"] = timezone.now()

        return super().validate(attrs)
