from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, Post, Comment, Like, Follow


# =========================
# REGISTER
# =========================

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):

    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    Profile.objects.get_or_create(user=user)

    return Response(
        {
            "message": "Registration successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        },
        status=status.HTTP_201_CREATED
    )


# =========================
# LOGIN
# =========================

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):

    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {"error": "Invalid username or password"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "Login successful",
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    })


# =========================
# PROFILE
# =========================

@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "GET":

        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "bio": profile.bio,
            "profile_picture": (
                request.build_absolute_uri(
                    profile.profile_picture.url
                )
                if profile.profile_picture
                else None
            ),
            "posts_count": Post.objects.filter(
                user=request.user
            ).count(),
            "followers_count": Follow.objects.filter(
                following=request.user
            ).count(),
            "following_count": Follow.objects.filter(
                follower=request.user
            ).count()
        })

    profile.bio = request.data.get(
        "bio",
        profile.bio
    )

    if "profile_picture" in request.FILES:
        profile.profile_picture = request.FILES[
            "profile_picture"
        ]

    profile.save()

    return Response({
        "message": "Profile updated successfully"
    })


# =========================
# ALL POSTS / CREATE POST
# =========================

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def posts(request):

    # GET POSTS
    if request.method == "GET":

        all_posts = Post.objects.all()

        result = []

        for post in all_posts:

            comments = []

            for comment in post.comments.all():

                comments.append({
                    "id": comment.id,
                    "username": comment.user.username,
                    "text": comment.text,
                    "created_at": comment.created_at
                })

            result.append({
                "id": post.id,
                "username": post.user.username,
                "content": post.content,
                "image": (
                    request.build_absolute_uri(
                        post.image.url
                    )
                    if post.image
                    else None
                ),
                "created_at": post.created_at,
                "likes_count": post.likes.count(),
                "comments": comments
            })

        return Response(result)

    # CREATE POST
    content = request.data.get("content", "")

    if not content and "image" not in request.FILES:
        return Response(
            {"error": "Post cannot be empty"},
            status=status.HTTP_400_BAD_REQUEST
        )

    post = Post.objects.create(
        user=request.user,
        content=content
    )

    if "image" in request.FILES:
        post.image = request.FILES["image"]
        post.save()

    return Response(
        {
            "message": "Post created successfully",
            "post_id": post.id
        },
        status=status.HTTP_201_CREATED
    )


# =========================
# DELETE POST
# =========================

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def