from cement.core.controller import CementBaseController, expose


class AppController(CementBaseController):
    class Meta:
        label = 'app'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Applications"

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()
