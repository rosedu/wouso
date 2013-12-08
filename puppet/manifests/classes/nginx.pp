class nginx {
    case $operatingsystem {
        'ubuntu': {
            package {
                ["nginx-full"]:
                    ensure => installed;
                    #before => File['/etc/nginx/sites-available/wouso'];
            }

            file {
                "/etc/nginx/sites-available/wouso":
                    content => template("${PROJ_DIR}/puppet/files/etc/nginx/sites-available/wouso"),
                    require => [Package['nginx-full']],
            }

            file {
                "/etc/nginx/fastcgi_params":
                    content => template("${PROJ_DIR}/puppet/files/etc/nginx/fastcgi_params"),
                    require => [Package['nginx-full']],
            }

            file {
                "/etc/nginx/sites-enabled/wouso":
                    ensure => "link",
                    target => "/etc/nginx/sites-available/wouso",
                    require => [File["/etc/nginx/sites-available/wouso"]],
            }

            file {
                "/etc/nginx/sites-enabled/default":
                    ensure => "absent",
                    require => [Package['nginx-full']],
            }

            exec {
                "reload-nginx":
                    command => "/usr/sbin/service nginx reload",
                    user => "root",
                    refreshonly => true,
            }

            service {
                "nginx":
                    ensure => running,
                    enable => true,
                    require => [Package["nginx-full"],
                                File["/etc/nginx/sites-enabled/wouso"],
                                File["/etc/nginx/fastcgi_params"]],
            }

        }
    }
}

