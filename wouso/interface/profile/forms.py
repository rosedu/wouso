from django import forms


class ChangePasswordForm(forms.Form):
    password1 = forms.CharField(max_length=30, label='New password',
                                    widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(max_length=30, label='Repeat new password',
                                    widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
