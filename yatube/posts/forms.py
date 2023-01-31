from django import forms

from .models import Comment, Post
from .utils import FormCleanMixin


class PostForm(forms.ModelForm, FormCleanMixin):
    """Form for create/edit post."""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm, FormCleanMixin):
    """Form for create comment."""
    class Meta:
        model = Comment
        fields = ('text',)
