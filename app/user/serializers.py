from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 4}}

    def create(self, data):
        return get_user_model().objects.create_user(**data)

    def update(self, instance, data):
        password = data.pop('password', None)
        user = super().update(instance, data)
        if password:
            user.set_password(password)
            user.save()

        return user

class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attr):
        email = attr.get('email')
        password = attr.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attr['user'] = user
        return attr

