# Cleanup old task definitions - keep only revisions 19 and 20
Write-Host "🧹 Cleaning up old task definitions..." -ForegroundColor Yellow

# Task definitions to keep
$keepRevisions = @(19, 20)

# Get all task definitions
$taskDefs = aws ecs list-task-definitions --family-prefix shine-api-gateway --status ACTIVE --query "taskDefinitionArns" --output text

foreach ($taskDef in $taskDefs.Split("`n")) {
    if ($taskDef) {
        # Extract revision number
        $revision = $taskDef.Split(":")[-1]
        
        if ($revision -notin $keepRevisions) {
            Write-Host "🗑️  Deleting task definition: shine-api-gateway:$revision" -ForegroundColor Red
            aws ecs deregister-task-definition --task-definition "shine-api-gateway:$revision"
        } else {
            Write-Host "✅ Keeping task definition: shine-api-gateway:$revision" -ForegroundColor Green
        }
    }
}

Write-Host "✨ Task definition cleanup complete!" -ForegroundColor Green
