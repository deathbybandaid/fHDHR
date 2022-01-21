Below you'll find the ramblings of deathbybandaid.

These are NOT documentation, and are subject to not always be valid.

However, since documentation is super hard for deathbybandaid, this may provide insight into things missing from the documentation.


# Running main.py

`python3 /home/sysop/fhdhr/main.py` (Program arguments discussed later)

At script start, a `SCRIPT_DIR` variable is set via pathlib to give the script the base directory that the script is being run from. This is the basis of other variables created and dynamically setup later.

Upon running, the internal `deps.Dependencies` will be imported and `SCRIPT_DIR` is passed to it. This package will read the `requirements.txt` file for dependencies, check for them, and install them if not. Preferably admins will manually install these. However, this system is included for potential development changes between updates.

If `gevent` is not able to import prior to the dependencies check, the script will respawn itself. The `monkey.patch_all()` function MUST run at the very beginning of fHDHR or the web server will have issues later.

At this point we import `fHDHR.cli.run` and `fHDHR_web`, and call the CLI system, passing through `SCRIPT_DIR`, `fHDHR_web`, and `deps` imports for use later.

# fHDHR CLI Arguments

Once `main.py` has triggered the real script to process, the first step is to process given arguments.

`-c`, `--config` are used to specify at PATH to a `config.ini`. This will default to `SCRIPT_DIR` + config.ini

`--setup` is used to generate a `config.ini` file. This will generate to the location decided by the `--config` argument; if given OR the default `SCRIPT_DIR` location.

`--iliketobreakthings` is really there for breaking things. This allows the bypass of normally non-configurable settings.

`-v`, `--version` should display the version.

# fHDHR order of operations

The first argument actually handled is `-v`, `--version`. This simply opens the `version.json` file and pulls the keys and values stored there, we then do a simple `print()` of this information with comma seperation.

Next we check if the admin used the `--setup` argument. This jumps to loading parts of the config system. By part, this will do a few things. Check for config file at given location via the `--config` argument (or default) and if not present will write the file at that location (touch). Then some basic directories will be 
