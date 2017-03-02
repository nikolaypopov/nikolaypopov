$vmCount=1
$async=$True
$vmObject="test"
$vmHost="10.3.199.151"
$vmDatastore="local-151"
$vmDisk=4000
$vmMemory=256
$vmCPU=2

echo "Total of $vmCount virtual machines will be created"

for ($i=1; $i -le $vmCount; $i++ ) {
	$vmName="$vmObject-$i"

	echo "Creating new virtual machine VM=$vmName ..."
	if ($async) {
		New-VM -Name $vmName -VMHost $vmHost -Datastore $vmDatastore -DiskMB $vmDisk -MemoryMB $vmMemory -NumCpu $vmCPU -RunAsync
	} else {
		New-VM -Name $vmName -VMHost $vmHost -Datastore $vmDatastore -DiskMB $vmDisk -MemoryMB $vmMemory -NumCpu $vmCPU
	}
}