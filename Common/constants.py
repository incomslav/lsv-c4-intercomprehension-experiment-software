__author__ = 'Muhammad Ahmad'
from django.utils.translation import ugettext_lazy as _


class CommonConstants:
    CONTINUE_BUTTON_TEXT = _("CONTINUE_BUTTON_TEXT")
    DELETE_BUTTON_TEXT = _("DELETE_BUTTON_TEXT")
    MINUTES_TEXT = _('MINUTES_TEXT')
    SECONDS_TEXT = _('SECONDS_TEXT')
    PLEASE_SELECT_A_LANGUAGE_TEXT = _("PLEASE_SELECT_A_LANGUAGE_TEXT")
    PLEASE_SELECT_COUNTRY_TEXT = _("PLEASE_SELECT_COUNTRY_TEXT")
    PLEASE_SELECT_GENDER_TEXT = _('PLEASE_SELECT_GENDER_TEXT')
    GENDER_MALE_TEXT = _('GENDER_MALE_TEXT')
    GENDER_FEMALE_TEXT = _('GENDER_FEMALE_TEXT')
    GENDER_NOT_SPECIFIED_TEXT = _('GENDER_NOT_SPECIFIED_TEXT')
    GOOD_LUCK_TEXT = _('GOOD_LUCK_TEXT')
    EXPERIMENT_FROM_LANGUAGE_LABEL = _('EXPERIMENT_FROM_LANGUAGE_LABEL')
    EXPERIMENT_TO_LANGUAGE_LABEL = _('EXPERIMENT_TO_LANGUAGE_LABEL')
    YES_TEXT = _('YES_TEXT')
    NO_TEXT = _('NO_TEXT')
    BACK_TO_EXPERIMENT_SELECTION = _('BACK_TO_EXPERIMENT_SELECTION')

    PleaseSelectUserName = "Please select username"
    SelectAll = "Select all"
    SelectGroup = "Select Group "


class NavBarConstants:
    """
    Navigation bar constants
    """
    NAVIGATION_BAR_HOME_BUTTON_TEXT = _("NAVIGATION_BAR_HOME_BUTTON_TEXT")
    NAVIGATION_BAR_USER_MENU_LOGOUT_TEXT = _("NAVIGATION_BAR_USER_MENU_LOGOUT_TEXT")
    BROWSER_TAB_TITLE_TEXT = _("BROWSER_TAB_TITLE_TEXT")


class LoginPageConstants:
    """
    Landing/Login and Register page constants
    """

    LANDING_PAGE_START_EXPERIMENT_HERE_TEXT = _("LANDING_PAGE_START_EXPERIMENT_HERE_TEXT")
    LANDING_PAGE_USERNAME_FIELD_TEXT = _("LANDING_PAGE_USERNAME_FIELD_TEXT")
    LANDING_PAGE_EMAIL_FIELD_TEXT = _("LANDING_PAGE_EMAIL_FIELD_TEXT")
    LANDING_PAGE_REGISTER_BUTTON_TEXT = _("LANDING_PAGE_REGISTER_BUTTON_TEXT")
    USER_REGISTRATION_PAGE_HEADER = _("USER_REGISTRATION_PAGE_HEADER")
    LANDING_PAGE_PASSWORD_FIELD_TEXT = _("LANDING_PAGE_PASSWORD_FIELD_TEXT")
    USER_REGISTRATION_PAGE_CONFIRM_PASSWORD_FIELD_TEXT = _("USER_REGISTRATION_PAGE_CONFIRM_PASSWORD_FIELD_TEXT")
    LANDING_PAGE_LOGIN_BUTTON_TEXT = _("LANDING_PAGE_LOGIN_BUTTON_TEXT")
    USER_REGISTRATION_PAGE_NEWS_LETTER_QUESTION = _("USER_REGISTRATION_PAGE_NEWS_LETTER_QUESTION")
    LOGIN_ERROR_MESSAGE = _("LOGIN_ERROR_MESSAGE")
    ACCOUNT_NOT_AVAILABLE_ERROR_MESSAGE = _("ACCOUNT_NOT_AVAILABLE_ERROR_MESSAGE")
    EMPTY_EMAIL_PASSWORD_ERROR_MESSAGE = _("EMPTY_EMAIL_PASSWORD_ERROR_MESSAGE")
    PASSWORD_MISMATCH_ERROR_MESSAGE = _("PASSWORD_MISMATCH_ERROR_MESSAGE")
    INVALID_EMAIL_ERROR_MESSAGE = _("INVALID_EMAIL_ERROR_MESSAGE")
    USERNAME_ALREADY_REGISTERED_ERROR_MESSAGE = _("USERNAME_ALREADY_REGISTERED_ERROR_MESSAGE")
    EMAIL_ALREADY_REGISTERED_ERROR_MESSAGE = _("EMAIL_ALREADY_REGISTERED_ERROR_MESSAGE")
    LANDING_PAGE_REMEMBER_ME_TEXT = _("LANDING_PAGE_REMEMBER_ME_TEXT")
    LANDING_PAGE_LOGIN_TO_CONTINUE_THE_CHALLENGE_TEXT = _("LANDING_PAGE_LOGIN_TO_CONTINUE_THE_CHALLENGE_TEXT")
    USER_ACCOUNT_ALREADY_EXISTS_AGAINST_PROVIDED_EMAIL_ERROR_MESSAGE = _(
        "USER_ACCOUNT_ALREADY_EXISTS_AGAINST_PROVIDED_EMAIL_ERROR_MESSAGE")
    INFORMED_CONSENT_MESSAGE_TEXT = _("INFORMED_CONSENT_MESSAGE_TEXT")
    INFORMED_CONSENT_I_AGREE_TEXT = _("INFORMED_CONSENT_I_AGREE_TEXT")
    INFORMED_CONSENT_ERROR_MESSAGE_TEXT = _("INFORMED_CONSENT_ERROR_MESSAGE_TEXT")
    INFORMED_CONSENT_PAGE_LINK_TEXT = _("INFORMED_CONSENT_PAGE_LINK_TEXT")


class LandingPageConstants:
    LanguageSelectionEn = "Please choose your language."
    LanguageSelectionDe = "Bitte w??hlen Sie Ihre Sprache aus."
    LanguageSelectionCs = "Prosz?? wybra?? j??zyk."
    LanguageSelectionPl = "Pros??m vyberte jazyk."
    LanguageSelectionRu = "????????????????????, ???????????????? ????????."
    LanguageSelectionBg = "???????? ???????????????? ????????."
    LanguageSelectionRs = "???????????? ?????? ?????????????????? ??????????."


class HomePageConstants:
    ChallengesRecommended = "Challenges recommended for you"


# Completed = _("Completed")
# NotYetStarted = _('not yet started')
# DoMoreChallengesToGetHigherCompletion = _('Do more challenges to get higher completion')
# Beginner = _("Beginner")
# Intermediate = _("Intermediate")
# Expert = _("Expert")
# RecentlyCompletedChallenges = _("Recently completed challenges")


class UserInfoPageConstants:
    """
    USER INFO PAGE CONSTANTS
    """
    USER_INFO_PAGE_HEADER = _("USER_INFO_PAGE_HEADER")
    USER_INFO_PAGE_AGE_TEXT = _("USER_INFO_PAGE_AGE_TEXT")
    USER_INFO_PAGE_GENDER_TEXT = _("USER_INFO_PAGE_GENDER_TEXT")
    USER_INFO_PAGE_LIVING_COUNTRY_QUESTION = _("USER_INFO_PAGE_LIVING_COUNTRY_QUESTION")
    USER_INFO_PAGE_LIVING_COUNTRY_LANGUAGE_QUESTION = _("USER_INFO_PAGE_LIVING_COUNTRY_LANGUAGE_QUESTION")
    USER_INFO_PAGE_ADD_ANOTHER_BUTTON_TEXT = _("USER_INFO_PAGE_ADD_ANOTHER_BUTTON_TEXT")
    USER_INFO_PAGE_LIVING_PERIOD_QUESTION = _("USER_INFO_PAGE_LIVING_PERIOD_QUESTION")
    USER_INFO_PAGE_LIVED_IN_ANOTHER_LANGUAGE_SPOKEN_AREA_QUESTION = _(
        "USER_INFO_PAGE_LIVED_IN_ANOTHER_LANGUAGE_SPOKEN_AREA_QUESTION")
    USER_INFO_PAGE_ANOTHER_AREA_LANGUAGE_QUESTION = _("USER_INFO_PAGE_ANOTHER_AREA_LANGUAGE_QUESTION")
    USER_INFO_PAGE_ANOTHER_AREA_LIVING_PERIOD_QUESTION = _("USER_INFO_PAGE_ANOTHER_AREA_LIVING_PERIOD_QUESTION")
    USER_INFO_PAGE_GROW_UP_MULTILINGUALLY_QUESTION = _("USER_INFO_PAGE_GROW_UP_MULTILINGUALLY_QUESTION")
    USER_INFO_PAGE_NATIVE_LANGUAGES_QUESTION = _("USER_INFO_PAGE_NATIVE_LANGUAGES_QUESTION")
    USER_INFO_PAGE_WHERE_DID_YOU_GO_TO_SCHOOL_QUESTION = _("USER_INFO_PAGE_WHERE_DID_YOU_GO_TO_SCHOOL_QUESTION")
    USER_INFO_PAGE_FOR_HOW_LONG_QUESTION = _("USER_INFO_PAGE_FOR_HOW_LONG_QUESTION")
    USER_INFO_PAGE_LANGUAGES_SPEAK_AT_HOME_QUESTION = _("USER_INFO_PAGE_LANGUAGES_SPEAK_AT_HOME_QUESTION")
    USER_INFO_PAGE_LIST_ALL_LEARNED_LANGUAGES_QUESTION = _("USER_INFO_PAGE_LIST_ALL_LEARNED_LANGUAGES_QUESTION")
    USER_INFO_PAGE_CONTINUE_BUTTON_TEXT = _("USER_INFO_PAGE_CONTINUE_BUTTON_TEXT")


class LanguageProficiencyPageConstants:
    """
    Language proficiency page constants
    """
    LANGUAGE_PROFICIENCY_PAGE_HEADER = _("LANGUAGE_PROFICIENCY_PAGE_HEADER")
    LANGUAGE_PROFICIENCY_PAGE_LEVEL_DESCRIPTION_HEADER = _("LANGUAGE_PROFICIENCY_PAGE_LEVEL_DESCRIPTION_HEADER")
    ZERO_TEXT = _("ZERO_TEXT")
    A_ONE_TEXT = _("A_ONE_TEXT")
    A_TWO_TEXT = _("A_TWO_TEXT")
    B_ONE_TEXT = _("B_ONE_TEXT")
    B_TWO_TEXT = _("B_TWO_TEXT")
    C_ONE_TEXT = _("C_ONE_TEXT")
    C_TWO_TEXT = _("C_TWO_TEXT")
    LANGUAGE_PROFICIENCY_PAGE_READING_SKILLS_TEXT = _("LANGUAGE_PROFICIENCY_PAGE_READING_SKILLS_TEXT")
    LANGUAGE_PROFICIENCY_PAGE_WRITING_SKILLS_TEXT = _("LANGUAGE_PROFICIENCY_PAGE_WRITING_SKILLS_TEXT")
    LANGUAGE_PROFICIENCY_PAGE_LISTENING_SKILLS_TEXT = _("LANGUAGE_PROFICIENCY_PAGE_LISTENING_SKILLS_TEXT")
    LANGUAGE_PROFICIENCY_PAGE_SPEAKING_SKILLS_TEXT = _("LANGUAGE_PROFICIENCY_PAGE_SPEAKING_SKILLS_TEXT")
    LANGUAGE_PROFICIENCY_PAGE_CONTINUE_BUTTON_TEXT = _("LANGUAGE_PROFICIENCY_PAGE_CONTINUE_BUTTON_TEXT")
    A_ONE_DESCRIPTION_TEXT = _("A_ONE_DESCRIPTION_TEXT")
    A_TWO_DESCRIPTION_TEXT = _("A_TWO_DESCRIPTION_TEXT")
    B_ONE_DESCRIPTION_TEXT = _("B_ONE_DESCRIPTION_TEXT")
    B_TWO_DESCRIPTION_TEXT = _("B_TWO_DESCRIPTION_TEXT")
    C_ONE_DESCRIPTION_TEXT = _("C_ONE_DESCRIPTION_TEXT")
    C_TWO_DESCRIPTION_TEXT = _("C_TWO_DESCRIPTION_TEXT")
    A_ONE_DESCRIPTION_DETAILS_TEXT = _("A_ONE_DESCRIPTION_DETAILS_TEXT")
    A_TWO_DESCRIPTION_DETAILS_TEXT = _("A_TWO_DESCRIPTION_DETAILS_TEXT")
    B_ONE_DESCRIPTION_DETAILS_TEXT = _("B_ONE_DESCRIPTION_DETAILS_TEXT")
    B_TWO_DESCRIPTION_DETAILS_TEXT = _("B_TWO_DESCRIPTION_DETAILS_TEXT")
    C_ONE_DESCRIPTION_DETAILS_TEXT = _("C_ONE_DESCRIPTION_DETAILS_TEXT")
    C_TWO_DESCRIPTION_DETAILS_TEXT = _("C_TWO_DESCRIPTION_DETAILS_TEXT")


# class MultipleChoicePageConstants:
# MultipleChoicesMessage = _("Multiple Choice")
#     SelectCorrectOptionMessage = _("Kindly select correct option:")


class PolishInDisguisePageConstants:
    """
    Polish in disguise page constants
    """
    POLISH_IN_DISGUISE_START_SCREEN_HEADER_TEXT = _("POLISH_IN_DISGUISE_STARTSCREEN_HEADER_TEXT")
    POLISH_IN_DISGUISE_ENTER_UNLOCK_CODE_TEXT = _("POLISH_IN_DISGUISE_ENTER_UNLOCK_CODE_TEXT")
    POLISH_IN_DISGUISE_UNLOCK_SCREEN_BUTTON_TEXT = _("POLISH_IN_DISGUISE_UNLOCK_SCREEN_BUTTON_TEXT")
    POLISH_IN_DISGUISE_START_SCREEN_I_AM_READY_TEXT = _("POLISH_IN_DISGUISE_STARTSCREEN_I_AM_READY_TEXT")
    POLISH_IN_DISGUISE_START_SCREEN_WAITING_FOR_PARTNER_TEXT = _(
        "POLISH_IN_DISGUISE_STARTSCREEN_WAITING_FOR_PARTNER_TEXT")
    POLISH_IN_DISGUISE_START_SCREEN_UNLOCK_CODE_DOES_NOT_MATCH_ERROR_TEXT = _(
        "POLISH_IN_DISGUISE_STARTSCREEN_UNLOCK_CODE_DOES_NOT_MATCH_ERROR_TEXT")
    POLISH_IN_DISGUISE_BOTH_READY_COUNTDOWN_TEXT = _("POLISH_IN_DISGUISE_BOTH_READY_COUNTDOWN_TEXT")

    POLISH_IN_DISGUISE_PAGE_HEADER = _("POLISH_IN_DISGUISE_PAGE_HEADER")
    POLISH_IN_DISGUISE_PAGE_TRANSLATE_PARAGRAPH_TEXT = _("POLISH_IN_DISGUISE_PAGE_TRANSLATE_PARAGRAPH_TEXT")
    POLISH_IN_DISGUISE_PAGE_CONTINUE_BUTTON_TEXT = _("POLISH_IN_DISGUISE_PAGE_CONTINUE_BUTTON_TEXT")
    POLISH_IN_DISGUISE_I_ACCEPT_TRANSLATION_TEXT = _("POLISH_IN_DISGUISE_I_ACCEPT_TRANSLATION_TEXT")
    POLISH_IN_DISGUISE_YOUR_PARTNER_TURN_TO_TYPE_TEXT = _("POLISH_IN_DISGUISE_YOUR_PARTNER_TURN_TO_TYPE_TEXT")
    POLISH_IN_DISGUISE_YOUR_TURN_TO_TYPE_TEXT = _("POLISH_IN_DISGUISE_YOUR_TURN_TO_TYPE_TEXT")
    POLISH_IN_DISGUISE_EXPERIMENT_INSTRUCTION_TEXT = _("POLISH_IN_DISGUISE_EXPERIMENT_INSTRUCTION_TEXT")


class MultilingualMessagesConstants:
    """
    multilingual messages constants
    """
    USER_INFORMATION_MISSING = _("USER_INFORMATION_MISSING")
    PLEASE_FILL_ALL_USER_INFO_FIELDS_ERROR_MESSAGE = _("PLEASE_FILL_ALL_USER_INFO_FIELDS_ERROR_MESSAGE")
    ARE_YOU_SURE_YOU_WANT_TO_DELETE_WARNING_MESSAGE = _("ARE_YOU_SURE_YOU_WANT_TO_DELETE_WARNING_MESSAGE")
    SELECT_PROFICIENCY_LEVEL_FOR_ALL_LANGUAGES_MESSAGE = _(
        "SELECT_PROFICIENCY_LEVEL_FOR_ALL_LANGUAGES_MESSAGE")
    SELECT_LANGUAGE_MESSAGE = _("SELECT_LANGUAGE_MESSAGE")
    PLEASE_LOGIN_MESSAGE = _("PLEASE_LOGIN_MESSAGE")
    PLEASE_SELECT_YOUR_NATIVE_LANGUAGE_MESSAGE = _("PLEASE_SELECT_YOUR_NATIVE_LANGUAGE_MESSAGE")
    INVALID_AGE_ERROR_MESSAGE = _("INVALID_AGE_ERROR_MESSAGE")
    ARE_YOU_SURE_YOU_WANT_TO_ACCEPT_THIS_TRANSLATION_ONCE_YOU_ACCEPT_YOU_CANT_CHANGE = _(
        "ARE_YOU_SURE_YOU_WANT_TO_ACCEPT_THIS_TRANSLATION_ONCE_YOU_ACCEPT_YOU_CANT_CHANGE")
    CLICK_ALL_WORDS_BEFORE_GETTING_NEW_SENTENCE_MESSAGE = _("CLICK_ALL_WORDS_BEFORE_GETTING_NEW_SENTENCE_MESSAGE")
    DO_NOT_NAVIGATE_AWAY_FROM_YOUR_BROWSER_MESSAGE = _("DO_NOT_NAVIGATE_AWAY_FROM_YOUR_BROWSER_MESSAGE")
    YOU_DID_NOT_ENTER_ANY_TRANSLATION_ARE_YOU_SURE_YOU_WANT_TO_SEE_NEXT_SENTENCE = _("YOU_DID_NOT_ENTER_ANY_TRANSLATION_ARE_YOU_SURE_YOU_WANT_TO_SEE_NEXT_SENTENCE")




class NoExperimentExistConstants:
    """
    experiment doesn't exist message constants
    """
    NO_EXPERIMENT_IS_AVAILABLE_TEXT = _("NO_EXPERIMENT_IS_AVAILABLE_TEXT")
    STAY_TUNED_TEXT = _("STAY_TUNED_TEXT")


class WebsiteLanguagesConstants:
    """
    website languages name constants
    """
    ENGLISH_LANGUAGE = _("ENGLISH_LANGUAGE")
    GERMAN_LANGUAGE = _("GERMAN_LANGUAGE")
    CZECH_LANGUAGE = _("CZECH_LANGUAGE")
    POLISH_LANGUAGE = _("POLISH_LANGUAGE")
    RUSSIAN_LANGUAGE = _("RUSSIAN_LANGUAGE")
    BULGARIAN_LANGUAGE = _("BULGARIAN_LANGUAGE")
    SERBIAN_LANGUAGE = _("SERBIAN_LANGUAGE")
    SLOVAK_LANGUAGE = _("SLOVAK_LANGUAGE")
    CROATIAN_LANGUAGE = _("CROATIAN_LANGUAGE")
    UKRAINIAN_LANGUAGE = _("UKRAINIAN_LANGUAGE")


class FreeTranslationWelcomePageConstants:
    """
    Free translation experiment welcome page constants
    """
    FREE_TRANSLATION_EXPERIMENT_WELCOME_HEADER = _("FREE_TRANSLATION_EXPERIMENT_WELCOME_HEADER")
    FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_TOTAL_WORDS_TEXT = _(
        "FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_TOTAL_WORDS_TEXT")
    FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_TIME_ESTIMATE_TEXT = _(
        "FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_TIME_ESTIMATE_TEXT")
    FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_HOW_FAST_ARE_YOU_TEXT = _(
        "FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_HOW_FAST_ARE_YOU_TEXT")
    FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_SET_KEYBOARD_LANGUAGE_TEXT = _(
        "FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_SET_KEYBOARD_LANGUAGE_TEXT")
    FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_CLOSE_BROWSER_WINDOWS_TEXT = _(
        "FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_CLOSE_BROWSER_WINDOWS_TEXT")
    FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_START_WHEN_READY_TEXT = _(
        "FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_START_WHEN_READY_TEXT")
    FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_CLICK_HERE_TO_SELECT_LANGUAGE_TEXT = _(
        "FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_CLICK_HERE_TO_SELECT_LANGUAGE_TEXT")
    FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_CONTINUE_BUTTON_TEXT = _(
        "FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_CONTINUE_BUTTON_TEXT")

    # Popup
    FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_SELECT_TRANSLATION_LANGUAGE_POPUP_HEADER = _(
        "FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_SELECT_TRANSLATION_LANGUAGE_POPUP_HEADER")
    FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_POPUP_SELECT_TRANSLATION_LANGUAGE_TEXT = _(
        "FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_POPUP_SELECT_TRANSLATION_LANGUAGE_TEXT")
    FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_CHOOSE_MOST_CONFIDENT_IN_LANGUAGE_TEXT = _(
        "FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_CHOOSE_MOST_CONFIDENT_IN_LANGUAGE_TEXT")
    FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_POPUP_CONTINUE_BUTTON_TEXT = _(
        "FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_POPUP_CONTINUE_BUTTON_TEXT")


class FreeTranslationPageConstants:
    """
    Free translation experiment page constants
    """
    FREE_TRANSLATION_TRANSLATE_WORD_TEXT = _("FREE_TRANSLATION_TRANSLATE_WORD_TEXT")
    # FREE_TRANSLATION_TRANSLATED_WORD_FIELD_TEXT = _("Type in")
    FREE_TRANSLATION_CONTINUE_BUTTON_TEXT = _("FREE_TRANSLATION_CONTINUE_BUTTON_TEXT")
    FREE_TRANSLATION_RESUME_AFTER_TEXT = _("FREE_TRANSLATION_RESUME_AFTER_TEXT")
    FREE_TRANSLATION_RESUME_NOW_BUTTON_TEXT = _("FREE_TRANSLATION_RESUME_NOW_BUTTON_TEXT")
    FREE_TRANSLATION_BREAK_TEXT = _("FREE_TRANSLATION_BREAK_TEXT")


class FreeTranslationCompletionPageConstants:
    """
    Free translation completion page constants
    """
    EXPERIMENT_FINAL_THANK_YOU_TEXT = _("EXPERIMENT_FINAL_THANK_YOU_TEXT")
    EXPERIMENT_FINAL_APPRECIATION_MESSAGE = _("EXPERIMENT_FINAL_APPRECIATION_MESSAGE")
    EXPERIMENT_FINAL_YOUR_RESULTS_HEADER = _("EXPERIMENT_FINAL_YOUR_RESULTS_HEADER")
    EXPERIMENT_FINAL_STATISTICS_HEADER = _("EXPERIMENT_FINAL_STATISTICS_HEADER")
    FINAL_TOTAL_WORDS_TEXT = _("FREE_TRANSLATION_FINAL_TOTAL_WORDS_TEXT")
    FINAL_CORRECT_TRANSLATIONS_TEXT = _("FREE_TRANSLATION_FINAL_CORRECT_TRANSLATIONS_TEXT")
    FINAL_TOTAL_TIME_TEXT = _("FREE_TRANSLATION_FINAL_TOTAL_TIME_TEXT")
    FINAL_TIME_PER_WORD_TEXT = _("FREE_TRANSLATION_FINAL_TIME_PER_WORD_TEXT")


class PhraseTranslationCompletionPageConstants:
    """
    Phrase translation completion page constants
    """
    EXPERIMENT_FINAL_THANK_YOU_TEXT = _("EXPERIMENT_FINAL_THANK_YOU_TEXT")
    EXPERIMENT_FINAL_APPRECIATION_MESSAGE = _("EXPERIMENT_FINAL_APPRECIATION_MESSAGE")
    EXPERIMENT_FINAL_YOUR_RESULTS_HEADER = _("EXPERIMENT_FINAL_YOUR_RESULTS_HEADER")
    EXPERIMENT_FINAL_STATISTICS_HEADER = _("EXPERIMENT_FINAL_STATISTICS_HEADER")
    FINAL_TOTAL_WORDS_TEXT = _("PHRASE_TRANSLATION_FINAL_TOTAL_PHRASES_TEXT")
    FINAL_CORRECT_TRANSLATIONS_TEXT = _("PHRASE_TRANSLATION_FINAL_CORRECT_TRANSLATIONS_TEXT")
    FINAL_TOTAL_TIME_TEXT = _("FREE_TRANSLATION_FINAL_TOTAL_TIME_TEXT")
    FINAL_TIME_PER_WORD_TEXT = _("PHRASE_TRANSLATION_FINAL_TIME_PER_PHRASE_TEXT")


class GapFillingCompletionPageConstants:
    """
    Gap filling experiment completion page constants
    """
    EXPERIMENT_FINAL_THANK_YOU_TEXT = _("EXPERIMENT_FINAL_THANK_YOU_TEXT")
    EXPERIMENT_FINAL_APPRECIATION_MESSAGE = _("EXPERIMENT_FINAL_APPRECIATION_MESSAGE")
    EXPERIMENT_FINAL_YOUR_RESULTS_HEADER = _("EXPERIMENT_FINAL_YOUR_RESULTS_HEADER")
    EXPERIMENT_FINAL_STATISTICS_HEADER = _("EXPERIMENT_FINAL_STATISTICS_HEADER")
    FINAL_TOTAL_WORDS_TEXT = _("GAP_FILLING_FINAL_TOTAL_SENTENCES_TEXT")
    FINAL_CORRECT_TRANSLATIONS_TEXT = _("GAP_FILLING_FINAL_CORRECT_TRANSLATIONS_TEXT")
    FINAL_TOTAL_TIME_TEXT = _("FREE_TRANSLATION_FINAL_TOTAL_TIME_TEXT")
    FINAL_TIME_PER_WORD_TEXT = _("GAP_FILLING_FINAL_TIME_PER_SENTENCE_TEXT")
    GAP_FILLING_FINAL_TOTAL_GAPS_TEXT = _("GAP_FILLING_FINAL_TOTAL_GAPS_TEXT")
    GAP_FILLING_FINAL_CORRECT_WORDS_TEXT = _("GAP_FILLING_FINAL_CORRECT_WORDS_TEXT")


class CloseTestExperimentPageConstants:
    WRITTEN_CLOZE_TEST_TEXT_EXPERIMENT_PAGE_INSTRUCTION_TIME = _("WRITTEN_CLOZE_TEST_TEXT_EXPERIMENT_PAGE_INSTRUCTION_TIME")