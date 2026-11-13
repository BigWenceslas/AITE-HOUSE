# -*- coding: utf-8 -*-
from . import controllers
from . import models


def _aite_post_init_hook(env):
    """ Rattache le canal « Chat du site » aux sites qui n'ont pas de chat. """
    env['website']._aite_setup_livechat_channel()
