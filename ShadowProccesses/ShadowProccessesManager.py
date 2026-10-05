import importlib
import os
import threading

from System.System import System


class ShadowProcessesManager:
    def __init__(self):
        self.UploadModelPlugins = ShadowProcessesManager.UploadModelPlugins()

    class UploadModelPlugins:
        thread = None
        BASE_PACKAGE = "System.plugins"  # имя пакета для import_module
        RELATIVE_PLUGIN_PATH = "../System/plugins"  # <-- сюда пиши относительный путь: "plugins", "../plugins", "sub/plugins" и т.д.

        loaded_modules = {}

        def __init__(self):
            self.thread = threading.Timer(interval=1, function=self.pluginsUpdate)
            self.run()

        def pluginsUpdate(self):
            # print("SHADOW RUNNED: pluginsUpdate")

            # base_dir — всегда абсолютный путь к папке текущего файла
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # собираем полный абсолютный путь к плагинам из base_dir + относительный кусок
            plugins_path = os.path.normpath(os.path.join(base_dir, self.RELATIVE_PLUGIN_PATH))

            for f in os.listdir(plugins_path):
                if f.endswith(".py") and f != "__init__.py" and f != "__TEMPLATE__.py":
                    name = f[:-3]
                    if name not in self.loaded_modules:
                        self.loaded_modules[name] = importlib.import_module(f"{self.BASE_PACKAGE}.{name}")
                        print(f"Загружен плагин: {name}  ")#,self.loaded_modules[name])
            System.AssetSubSystem.predictMethodsFromPluginFiles = self.loaded_modules
            self.thread.run()

        def run(self):
            self.thread.start()

        def stop(self):
            if self.thread and self.thread.is_alive():
                self.thread.cancel()