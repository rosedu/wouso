class git {
    case $operatingsystem {
        'ubuntu': {
            package {
                ["git"]:
                    ensure => installed;
            }
        }
    }
}


