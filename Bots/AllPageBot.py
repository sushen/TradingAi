""" Its a mixin class that mixed all Bot """
from Bots.bot_GropusPage import Bot_GroupPage
from Bots.bot_GroupMemberPage import Bot_GroupMemberPage
from Bots.bot_LoginPage import Bot_Login
from Bots.bot_MessagePage import Bot_MessagePage
from Bots.bot_ProfilePage import Bot_ProfilePage


class AllPageBot(
    Bot_Login,
    Bot_GroupPage,
    Bot_ProfilePage,
    Bot_MessagePage,
    Bot_GroupMemberPage
):
    pass
