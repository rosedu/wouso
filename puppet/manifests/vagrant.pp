import "classes/*.pp"

$APP_USER = "vagrant"
$PROJ_DIR = "/home/${APP_USER}/wouso"
$VENV_DIR = "/home/${APP_USER}/pybox"
$VENV_PY = "${VENV_DIR}/bin/python"

class dev {
    class {
        init: before => Class[python];
        python: before => Class[wouso];
        git: before => Class[wouso];
        nginx: before => Class[wouso];
        wouso:;
    }
}
include dev

