$vmName="test"
$async=$True

echo "All snapshots from VM=$vmName will be deleted"
if ($async) {
	Get-Snapshot $vmName | Remove-Snapshot -confirm:$false -RunAsync
} else {
	Get-Snapshot $vmName | Remove-Snapshot -confirm:$false
}shot $vmName | Remove-Snapshot -confirm:$false