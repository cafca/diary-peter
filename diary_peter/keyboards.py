#!/usr/bin/env python

"""Collection of custom keyboards."""

import logging

from telegram import KeyboardButton, ReplyKeyboardMarkup, Emoji, \
    InlineKeyboardButton, InlineKeyboardMarkup


def keyboard(name):
    """Return a custom keyboard."""
    try:
        buttons = globals()[name]
    except KeyError:
        logging.error("Custom keyboard {} not found.".format(name))
        return

    keyboard = [[KeyboardButton(button) for button in line]
        for line in buttons]
    rv = ReplyKeyboardMarkup(keyboard)
    return rv


def inline_keyboard(options):
    """Return an inline Keyboard given a dictionary of callback:display pairs."""
    rv = InlineKeyboardMarkup([[InlineKeyboardButton(v, callback_data=k)]
        for k, v in options.items()])
    return rv


"""Keyboard containing the hours from 5am-1pm."""
morning_hours = [
    ["5am", "6am", "7am"],
    ["8am", "9am", "10am"],
    ["11am", "12am", "1pm"],
]


"""A keyboard that just displays thumbs up and down."""
thumbs = [[Emoji.THUMBS_UP_SIGN, Emoji.THUMBS_DOWN_SIGN]]
