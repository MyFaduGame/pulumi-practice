import pulumi
from pulumi_azure_native import compute, network, resources

# 1. Create an Azure Resource Group
resource_group = resources.ResourceGroup(
    resource_name="TestingResourceGroup",
    location='eastus'
)

resource_group = resources.ResourceGroup("myResourceGroup",location='eastus')

# 2. Create a Virtual Network
vnet = network.VirtualNetwork(
    "myVnet",
    location='eastus',
    resource_group_name=resource_group.name,
    address_space=network.AddressSpaceArgs(address_prefixes=["10.0.0.0/16"])
)

# 3. Create a Subnet
subnet = network.Subnet(
    "mySubnet",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.1.0/24"
)

# 4. Create a Public IP Address
# public_ip = network.PublicIPAddress(
#     "freePublicIP",
#     location='eastus',
#     resource_group_name=resource_group.name,
#     public_ip_allocation_method="Dynamic",
#     sku=network.PublicIPAddressSkuArgs(
#         name="Basic" 
#     )
# )
# network.PublicIPAddress(
#     "myPublicIP",
#     location='eastus',
#     resource_group_name=resource_group.name,
#     public_ip_allocation_method="Dynamic"
# )

# 5. Create a Network Security Group with SSH Access
nsg = network.NetworkSecurityGroup(
    "myNSG",
    location='eastus',
    resource_group_name=resource_group.name,
    security_rules=[network.SecurityRuleArgs(
        name="allowSSH",
        priority=100,
        direction="Inbound",
        access="Allow",
        protocol="Tcp",
        source_port_range="*",
        destination_port_range="22",
        source_address_prefix="*",
        destination_address_prefix="*",
    )]
)

# 6. Create a Network Interface
nic = network.NetworkInterface(
    "myNIC",
    location='eastus',
    resource_group_name=resource_group.name,
    ip_configurations=[network.NetworkInterfaceIPConfigurationArgs(
        name="ipconfig1",
        subnet=network.SubnetArgs(id=subnet.id),
        private_ip_allocation_method="Dynamic",
        # public_ip_address=network.PublicIPAddressArgs(id=public_ip.id),
    )],
    network_security_group=network.NetworkSecurityGroupArgs(id=nsg.id)
)

# 7. Create the Virtual Machine
vm = compute.VirtualMachine(
    "myVM",
    location='eastus',
    resource_group_name=resource_group.name,
    network_profile=compute.NetworkProfileArgs(
        network_interfaces=[compute.NetworkInterfaceReferenceArgs(id=nic.id)]
    ),
    hardware_profile=compute.HardwareProfileArgs(vm_size="Standard_B1s"),
    os_profile=compute.OSProfileArgs(
        computer_name="myvm",
        admin_username="azureuser",
        admin_password="Pulumi123!",  # Use secrets in real projects
        linux_configuration=compute.LinuxConfigurationArgs(
            disable_password_authentication=False
        )
    ),
    storage_profile=compute.StorageProfileArgs(
        os_disk=compute.OSDiskArgs(
            create_option="FromImage",
            name="myOsDisk"
        ),
        image_reference=compute.ImageReferenceArgs(
            publisher="Canonical",
            offer="UbuntuServer",
            sku="18.04-LTS",
            version="latest"
        )
    )
)

# # 8. Export the public IP address
# pulumi.export("public_ip", public_ip.ip_address)
