import nonebot
import config
from os import path


if __name__ == '__main__':
    nonebot.init(config) #初始化QQ机器人然后加载配置文件
    nonebot.load_plugins(
        path.join(path.dirname(__file__),  'plugins'),
        'plugins'
    ) #加载内置的插件
    nonebot.run()




