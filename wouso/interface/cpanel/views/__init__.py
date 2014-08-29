class ModuleViewMixin(object):
    """
     This is exposing a module context variable in template, which is used to highlight the active tab/navigation link.
    """
    module = 'undefined'

    def get_context_data(self, **kwargs):
        context = super(ModuleViewMixin, self).get_context_data(**kwargs)
        context.update(dict(module=self.module))
        return context
