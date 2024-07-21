from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model, authenticate


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'password']

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            if not user.is_active:
                raise serializers.ValidationError("User is deactivated.")
            return user
        else:
            raise serializers.ValidationError("Invalid credentials.")
        

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id','title', 'description', 'date', 'organizer']
        read_only_fields = ['organizer']

    def create(self, validated_data):
        request = self.context.get('request')
        event = Event.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            date=validated_data['date'],
            organizer=request.user
        )
        return event


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Registration
        fields = ['id', 'user', 'event', 'registered_date']
        read_only_fields = ['user']

    def create(self, validated_data):
        
        request = self.context.get('request') 
        event = validated_data.get('event')
        registered_date = validated_data.get('registered_date')
        print('request:', request)
        print('event:', event)
        print('registered_date:', registered_date)

        if not Event.objects.filter(pk=event.id).exists():
            raise serializers.ValidationError("Event does not exist.")

        if Registration.objects.filter(user=request.user, event=event, registered_date=registered_date).exists():
            raise serializers.ValidationError("You are already registered for this event.")

        register_event = Registration.objects.create(
            user=request.user,
            event=event,
            registered_date=registered_date,

        )
        return register_event
