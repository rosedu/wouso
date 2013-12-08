class wouso {
    case $operatingsystem {
        'ubuntu': {
            package {
                ["libldap2-dev", "libsasl2-dev"]:
                    ensure => installed;
            }

            exec {
                "install-requirements":
                    cwd => "/home/${APP_USER}",
                    user => "${APP_USER}",
                    command => "${VENV_DIR}/bin/pip install -r ${PROJ_DIR}/requirements-pip",
            }

            exec {
                "install-flup":
                    cwd => "/home/${APP_USER}",
                    user => "${APP_USER}",
                    command => "${VENV_DIR}/bin/pip install flup",
            }

            exec {
                "copy-settings":
                    cwd => "${PROJ_DIR}/wouso",
                    user => "${APP_USER}",
                    command => "/bin/cp settings.py.example settings.py",
            }

            exec {
                "initial-setup":
                    cwd => "${PROJ_DIR}/wouso",
                    user => "${APP_USER}",
                    command => "${VENV_PY} manage.py wousoctl --setup --noinput",
                    require => [Exec['install-requirements'],
                                Exec['copy-settings']],
            }

            file {
                "/home/vagrant/fastcgi.bash":
                    content => template("${PROJ_DIR}/puppet/files/home/vagrant/fastcgi.bash"),
                    mode => '0744',
            }

            exec {
                "runserver":
                    cwd => "${PROJ_DIR}",
                    #user => "${APP_USER}",
                    user => "root",
                    command => "/home/vagrant/fastcgi.bash",
                    require => [Exec['initial-setup'],
                                Exec['install-flup'],
                                File['/home/vagrant/fastcgi.bash']],
            }

            cron {
                "wousocron":
                    command => "${VENV_PY} ${PROJ_DIR}/wouso/manage.py wousocron",
                    user => "${APP_USER}",
                    minute => 5,
                    environment => "PYTHONPATH=${PROJ_DIR}:${PROJ_DIR}/wouso/:\$PYTHONPATH",
            }

        }
    }
}


