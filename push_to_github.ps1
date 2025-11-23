# Script to push code to GitHub
# Run this after creating the repository on GitHub

Write-Host "`n🚀 Pushing to GitHub...`n"

# Check if repository exists
$repoUrl = "https://github.com/chakradharkalle03-arch/Semiconductor-Yield-Prediction-Optimization-Multi-Agent-System.git"
Write-Host "Repository URL: $repoUrl`n"

# Push to GitHub
Write-Host "Pushing code to main branch...`n"
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Successfully pushed to GitHub!`n"
    Write-Host "🌐 View your repository at:`n"
    Write-Host "   https://github.com/chakradharkalle03-arch/Semiconductor-Yield-Prediction-Optimization-Multi-Agent-System`n"
} else {
    Write-Host "`n⚠️ Push failed. Common reasons:`n"
    Write-Host "   - Repository doesn't exist yet (create it first)`n"
    Write-Host "   - Authentication required (use Personal Access Token)`n"
    Write-Host "   - Network issues`n"
    Write-Host "`n💡 To create repository:`n"
    Write-Host "   1. Go to https://github.com/new`n"
    Write-Host "   2. Name: Semiconductor-Yield-Prediction-Optimization-Multi-Agent-System`n"
    Write-Host "   3. Don't initialize with README/gitignore/license`n"
    Write-Host "   4. Click Create repository`n"
    Write-Host "   5. Run this script again`n"
}

