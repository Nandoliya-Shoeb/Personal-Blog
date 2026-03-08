from django import forms
from .models import Post, Comment, Category


class PostForm(forms.ModelForm):
    """Form for creating and editing blog posts"""
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select a category",
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'category', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter post title',
                'maxlength': '300'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Write your post content here...',
                'rows': 12
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            })
        }

    def clean_title(self):
        """Validate title"""
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError('Title is required.')
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters long.')
        return title

    def clean_content(self):
        """Validate content"""
        content = self.cleaned_data.get('content')
        if not content:
            raise forms.ValidationError('Content is required.')
        if len(content) < 50:
            raise forms.ValidationError('Content must be at least 50 characters long.')
        return content


class CommentForm(forms.ModelForm):
    """Form for creating comments"""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Write your comment here...',
                'rows': 4,
                'required': True
            })
        }

    def clean_content(self):
        """Validate comment content"""
        content = self.cleaned_data.get('content')
        if not content:
            raise forms.ValidationError('Comment cannot be empty.')
        if len(content) < 2:
            raise forms.ValidationError('Comment must be at least 2 characters.')
        return content


class PostSearchForm(forms.Form):
    """Form for searching posts"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Search posts by title or content...',
            'autocomplete': 'off'
        })
    )
