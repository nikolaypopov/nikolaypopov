$cloneCount=2
$async=$True
$vmName = "test-1"
$cloneObject="$vmName-clone"
$datastoreName="local-151"
$hostName="10.3.199.151"

echo "Total of $cloneCount clones will be created"

for ($i=1; $i -le $cloneCount; $i++) {
	$cloneName="$cloneObject-$i"

	echo "Cloning $vmName to a new virtual machine VM=$cloneName ..."
	if ($async) {
		New-VM -Name $cloneName -VM $vmName -Datastore $datastoreName -VMHost $hostName -RunAsync
	} else {
		New-VM -Name $cloneName -VM $vmName -Datastore $datastoreName -VMHost $hostName
	}
}