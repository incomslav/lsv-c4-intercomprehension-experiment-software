__author__ = 'Muhammad Ahmad'
from Common import constants
from django import template

from Incomslav.settings import LANGUAGES

register = template.Library()


@register.simple_tag
def site_languages():
    """
    Navigation bar site language selection menu
    :return:
    """
    response = ""

    for i,(code, name) in enumerate(LANGUAGES):
        style = str("background-image: url(/static/images/flags/{}.png);background-repeat: no-repeat;background-position: 90% 50%;").format(code)
        span = str("<span id='spn_{}'>{}</span>").format(code, name)
        response += str("<li><a onclick='changeWebLanguageAjaxRequest({});' style='{}'>{}</a></li>").format(str(i), style, span)
    return response

@register.simple_tag
def nav_bar():
    """
    navigation bar
    :return:
    """
    return constants.NavBarConstants.NAVIGATION_BAR_HOME_BUTTON_TEXT

@register.simple_tag
def nav_bar_user_menu():
    """
    navigation bar user menu
    :return:
    """
    return constants.NavBarConstants.NAVIGATION_BAR_USER_MENU_LOGOUT_TEXT

@register.simple_tag
def browser_tab_title():
    """
    Browser tab title
    :return:
    """
    return constants.NavBarConstants.BROWSER_TAB_TITLE_TEXT
