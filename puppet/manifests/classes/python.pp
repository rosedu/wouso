class python {
    case $operatingsystem {
        'ubuntu': {
            package {
                ["python-dev", "python", "python-virtualenv", "python-pip"]:
                    ensure => installed;
            }

            exec {
                "virtualenv-create":
                    cwd => "/home/${APP_USER}",
                    user => "${APP_USER}",
                    command => "/usr/bin/virtualenv ${VENV_DIR}",
                    creates => $VENV_DIR
            }
        }
    }
}

