from ....text import parts as tp
from ...queries.binary import Binary
from ...queries.binary import BinaryOps
from ...queries.rendering import Renderer
from ...queries.rendering import StdRenderer


##


class MysqlRenderer(StdRenderer):
    """
    Standard rendering plus MySQL's structural divergences. Identifier quoting (backticks) and param style are *not*
    here - they ride on the queries.Adapter as config; only genuine structural differences live in this subclass.
    """

    @Renderer.render.register
    def render_binary(self, o: Binary) -> tp.Part:
        # MySQL has no `||` string-concat operator by default - it is the `concat(...)` function.
        if o.op is BinaryOps.CONCAT:
            return tp.Concat([
                'concat',
                tp.Wrap(tp.List([self.render(o.l), self.render(o.r)])),
            ])

        return super().render_binary(o)
