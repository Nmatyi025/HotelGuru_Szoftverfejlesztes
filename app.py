from flask import Flask
from config import Config
from WebApp import create_app

if __name__ == '__main__':
    create_app(config_class=Config).run("localhost", 8888)
