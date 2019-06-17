from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse


def jinja2_environment(**options):
    """
    确保可以使用模版引擎中的{{url('')}} {{static('')}}
    :param options:
    :return:
    """
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
    })

    return env