import os
import sys
import traceback

import ringzauber_intro
import ringzauber

def main():
    try:
        # Persistent app data directory
        appdata = os.getenv("APPDATA")
        app_dir = os.path.join(appdata, "Ringzauber")
        os.makedirs(app_dir, exist_ok=True)

        first_run_flag = os.path.join(app_dir, "first_run_done.flag")

        if not os.path.exists(first_run_flag):
            # FIRST RUN → intro
            ringzauber_intro.main()


            # Mark intro as done
            with open(first_run_flag, "w") as f:
                f.write("done")

        # ALWAYS start main app
        ringzauber.run_application()

    except Exception:
        print("An unhandled exception occurred:")
        traceback.print_exc()
        input("Press Enter to close...")

if __name__ == "__main__":
    main()
