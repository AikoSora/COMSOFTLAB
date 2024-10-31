from django.views import View
from django.shortcuts import render

from .models import Mail


class HomePage(View):

    def get(self, request):

        return render(
            request=request,
            template_name='index.html',
            context=dict(
                mails=Mail.objects.all().order_by('-mail_id'),
            )
        )


__all__ = (
    'HomePage',
)
