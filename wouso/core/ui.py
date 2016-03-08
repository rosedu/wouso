from django.db import models
from wouso.core.game.models import Game


class BlockLibrary(object):
    def __init__(self):
        self.parts = {}

    def get_blocks(self):
        return self.parts.keys()

    def get_block(self, key, context):
        block = self.parts.get(key, '')
        if callable(block):
            return block(context)
        return block

    def add(self, key, callback):
        self.parts[key] = callback


_libraries = {}


def get_library(library):
    global _libraries
    if not _libraries.get(library, None):
        _libraries[library] = BlockLibrary()
    return _libraries[library]


def get_sidebar():
    return get_library('sidebar')


def get_header():
    return get_library('header')


def get_footer():
    return get_library('footer')


def register_block(library, name, callback):
    lib = get_library(library)
    lib.add(name, callback)


def register_sidebar_block(name, callback):
    return register_block('sidebar', name, callback)


def register_header_link(name, callback):
    return register_block('header', name, callback)


def register_footer_link(name, callback):
    return register_block('footer', name, callback)
