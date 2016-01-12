# -*- coding: utf-8 -*-

import click


@click.command(
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True
    },
    add_help_option=False
)
@click.pass_context
def serve(ctx):
    """
    # start app from current dir
    """
    from .. import runner
    runner.serve()


if __name__ == '__main__':
    # pylint: disable=E1120
    serve()
