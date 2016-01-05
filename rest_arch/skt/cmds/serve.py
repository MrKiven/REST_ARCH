# -*- coding: utf-8 -*-

import click

from ...app import make_app


@click.command(
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True
    },
    add_help_option=False
)
@click.pass_context
def serve(ctx):
    app = make_app('test')
    app.run()


if __name__ == '__main__':
    # pylint: disable=E1120
    serve()
