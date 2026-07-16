import traceback
import runpy

try:
    runpy.run_path('d:/Projects/game/main.py', run_name='__main__')
except SystemExit as e:
    print("SystemExit:", e.code)
except Exception as e:
    traceback.print_exc()
