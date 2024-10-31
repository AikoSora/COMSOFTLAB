from django.views import View
from django.shortcuts import render


class HomePage(View):

    def get(self, request):

        return render(
            request=request,
            template_name='index.html',
        )


__all__ = (
    'HomePage',
)
