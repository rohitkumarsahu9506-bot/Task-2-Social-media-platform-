from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile, Post, Comment, Like, Follow


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )

        Profile.objects.create(user=user)

        return user


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id',
            'user',
            'bio',
            'profile_picture'
        ]


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'user',
            'text',
            'created_at'
        ]
        read_only_fields = ['user']


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'user',
            'content',
            'image',
            'created_at',
            'comments',
            'likes_count'
        ]
        read_only_fields = ['user']

    def get_likes_count(self, obj):
        return obj.likes.count()


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = [
            'id',
            'follower',
            'following',
            'created_at'
        ]