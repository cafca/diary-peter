#!/usr/bin/env python

"""Collection of custom keyboards."""

from telegram import KeyboardButton, ReplyKeyboardMarkup, Emoji


def morning_hours():
    """Return a custom keyboard containing the hours from 5am-1pm."""
    buttons = [
        ["5am", "6am", "7am"],
        ["8am", "9am", "10am"],
        ["11am", "12am", "1pm"],
    ]
    keyboard = [[KeyboardButton(button) for button in line]
        for line in buttons]
    return ReplyKeyboardMarkup(keyboard)


def thumbs():
    """A keyboard that just displays thumbs up and down."""
    buttons = [[Emoji.THUMBS_UP_SIGN, Emoji.THUMBS_DOWN_SIGN]]
    keyboard = [[KeyboardButton(button) for button in line]
        for line in buttons]
    return ReplyKeyboardMarkup(keyboard)
