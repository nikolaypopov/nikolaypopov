$vmCount=1
$async=$True
$vmObject="test"

echo "Total of $vmCount virtual machines will be deleted"

for ($i=1; $i -le $vmCount; $i++ ) {
	$vmName="$vmObject-$i"

	echo "Deleting virtual machine VM=$vmName from disk ..."
	if ($async) {
		Remove-VM $vmName -DeletePermanently -confirm:$false -RunAsync
	} else {
		Remove-VM $vmName -DeletePermanently -confirm:$false
	}
}