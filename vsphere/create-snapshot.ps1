$ssCount=1
$async=$True
$vmName="test"
$ssObject="ss"

echo "Total of $ssCount snapshots on VM=$vmName will be created"

for ($i=1; $i -le $ssCount; $i++ ) {
	$ssName="$ssObject-$i"

	echo "Creating snapshot=$vmName on VM=$vmName ..."
	if ($async) {
		New-Snapshot -VM $vmName -Name $ssName -RunAsync

	} else {
		New-Snapshot -VM $vmName -Name $ssName
	}
}