#!/usr/bin/env python

"""Collection of custom keyboards."""

# Copyright 2016 Vincent Ahrend

#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
