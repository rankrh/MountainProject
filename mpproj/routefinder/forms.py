from django import forms

class SortMethod(forms.Form):
    sort = forms.ChoiceField(
        choices=[
            ('distance', 'Distance'),
            ('area_group', 'Area'),
            ('style', 'Style'),
            ('bayes', 'Rating'),
            ('value', 'Relevance')
        ],
        widget=forms.RadioSelect(
            attrs={
                'class': 'sort-method'},
        ))

