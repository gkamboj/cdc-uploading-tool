from flask import render_template

from config.configuration import configs


def home():
    return render_template('layout.html', configs=configs, is_homepage=True)


def translate():
    return render_template('translate.html', configs=configs)


def config():
    return render_template('config.html', configs=configs)


def upload():
    return render_template('upload.html', configs=configs)


def template_creation():
    return render_template('template_creation.html', configs=configs)
