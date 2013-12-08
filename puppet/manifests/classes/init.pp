class init {
    group {
        "puppet":
            ensure => "present",
    }

    user {
        $APP_USER:
            ensure => "present",
            managehome => true,
    }

    if $operatingsystem == "ubuntu" {
        exec {
            "update_apt":
                command => "/usr/bin/sudo apt-get update",
        }
        file {
            "/home/vagrant/.bashrc":
                content => template("${PROJ_DIR}/puppet/files/home/vagrant/.bashrc"),
                mode => '0744',
        }

    }
}

