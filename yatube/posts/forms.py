from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст',
            'group': 'Группа',
            'image': 'Картинка',
        }
        help_texts = {
            'text': 'Содержание',
            'group': 'Категория',
            'image': 'Изображение',
        }

    def empty_text(self):
        data = self.cleaned_data['text']

        if not data:
            raise forms.ValidationError('Текст должен быть заполнен!')

        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Комментарий'}
        help_texts = {'text': 'Кузница мнений'}

    def empty_text(self):
        data = self.cleaned_data['text']

        if not data:
            raise forms.ValidationError('Необходима наполненность!')

        return data
