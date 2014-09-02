MOUNT_POINT = '/home/vagrant/wouso'

Vagrant.configure("2") do |config|
    config.vm.box = "precise64"
    config.vm.box_url = "http://files.vagrantup.com/precise64.box"

    config.vm.synced_folder ".", MOUNT_POINT, create: true, mount_options: ["dmode=775,fmode=664"]
    config.vm.network "forwarded_port", guest: 80, host: 8000
    #config.vm.network :hostonly, "1.2.3.4"

    config.vm.provision "puppet" do |puppet|
        puppet.manifests_path = "puppet/manifests"
        puppet.manifest_file = "vagrant.pp"
    end
end

