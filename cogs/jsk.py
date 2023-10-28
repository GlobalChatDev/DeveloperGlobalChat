import traceback

from discord.ext import commands
from jishaku.codeblocks import codeblock_converter
from jishaku.cog import OPTIONAL_FEATURES, STANDARD_FEATURES
from jishaku.exception_handling import ReplResponseReactor
from jishaku.features.baseclass import Feature
from jishaku.functools import AsyncSender
from jishaku.repl import AsyncCodeExecutor
from jishaku.repl.repl_builtins import get_var_dict_from_ctx

# look into making more jishaku commands: https://jishaku.readthedocs.io/en/latest/cog.html


class Jishaku(*OPTIONAL_FEATURES, *STANDARD_FEATURES):
    async def cog_command_error(self, ctx, error):
        if ctx.command and not ctx.command.has_error_handler():
            await ctx.send(error)
            traceback.print_exc()


    @Feature.Command(parent="jsk", name="py", aliases=["python"])
    async def jsk_python(self, ctx: commands.Context, *, argument: codeblock_converter): # type: ignore

        arg_dict = get_var_dict_from_ctx(ctx, "")
        arg_dict.update(get_var_dict_from_ctx(ctx, "_"))
        arg_dict["owners"] = {await ctx.bot.try_user(oid) for oid in ctx.bot.owner_ids}
        arg_dict["_"] = self.last_result

        scope = self.scope

        try:
            async with ReplResponseReactor(ctx.message):
                with self.submit(ctx):
                    executor = AsyncCodeExecutor(argument.content, scope, arg_dict=arg_dict)
                    async for send, result in AsyncSender(executor): # type: ignore
                        if result is None:
                            continue

                        self.last_result = result

                        send(await self.jsk_python_result_handling(ctx, result))

        finally:
            scope.clear_intersection(arg_dict)


async def setup(bot: commands.Bot):
    await bot.add_cog(Jishaku(bot=bot))
