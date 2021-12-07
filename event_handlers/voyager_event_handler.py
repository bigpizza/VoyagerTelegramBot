from typing import List
from typing import Dict
from telegram import TelegramBot


class VoyagerEventHandler:
    """A base class for all event handlers to inherit from.

    To handle an incoming event from voyager application server, Most important method is the 'handle_event' method.
    """

    def __init__(self, event_names: List[str], telegram_bot: TelegramBot):
        print('init voyager event handler')

    @staticmethod
    def interested_event_names():
        """
        :return: List of event names this event_handler wants to process.
        """
        return []

    @staticmethod
    def interested_event_name():
        """
        :return: An event name this event_handler wants to process.
        """
        return None

    def handle_event(self, event_name: str, message: Dict):
        """
        Processes the incoming event + message. Note: a single message might be
        processed by multiple event handlers. Don't modify the message dict.
        :param event_name: The event name in string format.
        :param message: A dictionary containing all messages
        :return: Nothing
        """
        print('handling event', event_name, message)
