from django import forms
from todo.models import Todo, Goal


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'priority', 'status', 'tag', 'goal']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
        # Filter goals to only show the user's goals
        if user:
            self.fields['goal'].queryset = Goal.objects.filter(user=user)