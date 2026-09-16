from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register),
    path("login/", views.login),
    path("logout/", views.logout),

    path("profile/", views.profile),

    path("posts/", views.posts),
    path("posts/<int:post_id>/delete/", views.delete_post),
    path("posts/<int:post_id>/comment/", views.add_comment),
    path("posts/<int:post_id>/like/", views.like_post),

    path("users/<int:user_id>/follow/", views.follow_user),
    path("users/", views.users),
]