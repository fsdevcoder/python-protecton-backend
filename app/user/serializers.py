from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from score.serializers import ScoreSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    scores_initial = ScoreSerializer(many=False)
    scores_final = ScoreSerializer(many=False)

    class Meta:
        model = get_user_model()
        fields = ('phone_number', 'password', 'name', 'scores_initial',
                  'scores_final', 'first_name', 'last_name', 'age',
                  'zipcode', 'income', 'education', 'employment')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    phone_number = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        user = authenticate(
            requests=self.context.get('request'),
            username=phone_number,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
