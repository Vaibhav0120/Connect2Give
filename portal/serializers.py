# portal/serializers.py
from rest_framework import serializers
from .models import User, NGOProfile, VolunteerProfile, RestaurantProfile

class RestaurantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantProfile
        fields = ['restaurant_name', 'address', 'phone_number']

class VolunteerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerProfile
        fields = ['full_name', 'phone_number', 'skills']

class NGOProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NGOProfile
        fields = ['ngo_name', 'registration_number', 'address', 'contact_person']

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, including nested profiles.
    This handles the logic for creating users with different roles.
    """
    restaurant_profile = RestaurantProfileSerializer(required=False)
    ngo_profile = NGOProfileSerializer(required=False)
    volunteer_profile = VolunteerProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'user_type', 'restaurant_profile', 'ngo_profile', 'volunteer_profile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user_type = validated_data.get('user_type')
        restaurant_profile_data = validated_data.pop('restaurant_profile', None)
        ngo_profile_data = validated_data.pop('ngo_profile', None)
        volunteer_profile_data = validated_data.pop('volunteer_profile', None)

        # Create the user instance
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=user_type
        )

        # Create the corresponding profile based on user_type
        if user_type == User.UserType.RESTAURANT and restaurant_profile_data:
            RestaurantProfile.objects.create(user=user, **restaurant_profile_data)
        elif user_type == User.UserType.NGO and ngo_profile_data:
            NGOProfile.objects.create(user=user, **ngo_profile_data)
        elif user_type == User.UserType.VOLUNTEER and volunteer_profile_data:
            VolunteerProfile.objects.create(user=user, **volunteer_profile_data)
        
        return user