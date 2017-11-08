import discord, aiohttp
from discord.ext import commands
from ext import embeds_coc
import json
from __main__ import InvalidTag
from ext.paginator import PaginatorSession
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import io
import string


class TagCheck(commands.MemberConverter):

    async def convert(self, ctx, argument):
        # Try to convert it to a member.
        try:
            user = await super().convert(ctx, argument)
        except commands.BadArgument:
            pass 
        else:
            return user

        # Not a user so its a tag.
        return argument.strip('#').upper()

class COC_Stats:

    def __init__(self, bot):
        self.bot = bot
        with open('data/config.json') as config:
            self.session = aiohttp.ClientSession(
                headers={
                'Authorization': f"Bearer {json.load(config)['coc-token']}"
                })
        self.conv = TagCheck()


    async def get_clan_from_profile(self, ctx, tag, message):
        async with self.session.get(f"https://api.clashofclans.com/v1/players/%23{tag}") as p:
            profile = await p.json()
        try:
            clan_tag = profile['clan']
        except KeyError:
            await ctx.send(message)
            raise ValueError(message)
        else:
            return clan_tag


    async def resolve_tag(self, ctx, tag_or_user, clan=False):
        if not tag_or_user:
            try:
                tag = ctx.get_tag('clashofclans')
            except Exception as e:
                print(e)
                await ctx.send('You don\'t have a saved tag.')
                raise e
            else:
                if clan is True:
                    return await self.get_clan_from_profile(ctx, tag, 'You don\'t have a clan!')
                return tag
        if isinstance(tag_or_user, discord.Member):
            try:
                tag = ctx.get_tag('clashofclans', tag_or_user.id)
            except KeyError as e:
                await ctx.send('That person doesnt have a saved tag!')
                raise e
            else:
                if clan is True:
                    return await self.get_clan_from_profile(ctx, tag, 'That person does not have a clan!')
                return tag
        else:
            return tag_or_user

    @commands.group(invoke_without_command=True)
    async def cocprofile(self, ctx, *, tag_or_user: TagCheck=None):
        '''Gets the Clash of Clans profile of a player.'''
        tag = await self.resolve_tag(ctx, tag_or_user)

        async with ctx.typing():
            try:
                async with self.session.get(f"https://api.clashofclans.com/v1/players/%23{tag}") as p:
                    profile = await p.json()
            except Exception as e:
                return await ctx.send(f'`{e}`')
            else:
                em = await embeds_coc.format_profile(ctx, profile)
                await ctx.send(embed=em)


    # @commands.group(invoke_without_command=True)
    # async def clan(self, ctx, *, tag_or_user: TagCheck=None):
    #     '''Gets a clan by tag or by profile. (tagging the user)'''
    #     tag = await self.resolve_tag(ctx, tag_or_user, clan=True)

    #     await ctx.trigger_typing()
    #     try:
    #         clan = await self.cr.get_clan(tag)
    #     except Exception as e:
    #         return await ctx.send(f'`{e}`')
    #     else:
    #         ems = await embeds.format_clan(ctx, clan)
    #         session = PaginatorSession(
    #             ctx=ctx,
    #             pages=ems
    #             )
    #         await session.run()

    # @commands.group(invoke_without_command=True)
    # async def members(self, ctx, *, tag_or_user: TagCheck=None):
    #     '''Gets all the members of a clan.'''
    #     tag = await self.resolve_tag(ctx, tag_or_user, clan=True)

    #     await ctx.trigger_typing()
    #     try:
    #         clan = await self.cr.get_clan(tag)
    #     except Exception as e:
    #         return await ctx.send(f'`{e}`')
    #     else:
    #         ems = await embeds.format_members(ctx, clan)
    #         if len(ems) > 1:
    #             session = PaginatorSession(
    #                 ctx=ctx, 
    #                 pages=ems, 
    #                 footer_text=f'{len(clan.members)}/50 members'
    #                 )
    #             await session.run()
    #         else:
    #             await ctx.send(embed=ems[0])

    # @members.command()
    # async def best(self, ctx, *, tag_or_user: TagCheck=None):
    #     '''Finds the best members of the clan currently.'''
    #     tag = await self.resolve_tag(ctx, tag_or_user, clan=True)
    #     async with ctx.typing():
    #         try:
    #             clan = await self.cr.get_clan(tag)
    #         except Exception as e:
    #             return await ctx.send(f'`{e}`')
    #         else:
    #             if len(clan.members) < 4:
    #                 return await ctx.send('Clan must have more than 4 players for heuristics.')
    #             else:
    #                 em = await embeds.format_most_valuable(ctx, clan)
    #                 await ctx.send(embed=em)

    # @members.command()
    # async def worst(self, ctx, *, tag_or_user: TagCheck=None):
    #     '''Finds the worst members of the clan currently.'''
    #     tag = await self.resolve_tag(ctx, tag_or_user, clan=True)
    #     async with ctx.typing():
    #         try:
    #             clan = await self.cr.get_clan(tag)
    #         except Exception as e:
    #             return await ctx.send(f'`{e}`')
    #         else:
    #             if len(clan.members) < 4:
    #                 return await ctx.send('Clan must have more than 4 players for heuristics.')
    #             else:
    #                 em = await embeds.format_least_valuable(ctx, clan)
    #                 await ctx.send(embed=em)

            
    @commands.command()
    async def cocsave(self, ctx, *, tag):
        '''Saves a Clas of Clans tag to your discord.

        Ability to save multiple tags coming soon.
        '''
        ctx.save_tag(tag.replace("#", ""), 'clashofclans')
        await ctx.send('Successfuly saved tag.')


def setup(bot):
    cog = COC_Stats(bot)
    bot.add_cog(cog)
