MOUNT_POINT = '/home/vagrant/wouso'

Vagrant::Config.run do |config|
    config.vm.box = "precise64"
    config.vm.box_url = "http://files.vagrantup.com/precise64.box"

    config.vm.share_folder "repo-root", MOUNT_POINT, ".", :create => true
    config.vm.forward_port 80, 8000
    #config.vm.network :hostonly, "1.2.3.4"

    config.vm.provision :puppet do |puppet|
        puppet.manifests_path = "puppet/manifests"
        puppet.manifest_file = "vagrant.pp"
    end
end

