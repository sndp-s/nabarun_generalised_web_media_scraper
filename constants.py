"""
The environment variables utils
"""
from environs import Env


env = Env()
env.read_env()

AUTHOR = env("AUTHOR")
