from django import forms
from .models import ReviewRating

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']

    def clean_review(self):
        review = self.cleaned_data.get('review')
        if len(review) > 500:  # Kiểm tra giới hạn ký tự
            raise forms.ValidationError("Review không được vượt quá 500 ký tự.")
        return review