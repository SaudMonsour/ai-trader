# GitHub Branch Protection Setup

## Prerequisites
- GitHub CLI (`gh`) installed
- Repository admin access

## Option 1: Using GitHub CLI

Replace `:owner` and `:repo` with your repository details.

### Protect 'staging' branch
```bash
gh api repos/:owner/:repo/branches/staging/protection \
  -X PUT \
  -f required_status_checks='{"strict": true, "contexts": ["CI"]}' \
  -f required_pull_request_reviews='{"required_approving_review_count": 1}' \
  -f enforce_admins=true \
  -f restrictions=null
```

### Protect 'main' branch
```bash
gh api repos/:owner/:repo/branches/main/protection \
  -X PUT \
  -f required_status_checks='{"strict": true, "contexts": ["CI"]}' \
  -f required_pull_request_reviews='{"required_approving_review_count": 1}' \
  -f enforce_admins=true \
  -f restrictions=null
```

## Option 2: Using GitHub Web UI

1. Navigate to: **Settings** → **Branches** → **Add rule**

2. **Branch name pattern**: `staging` (or `main`)

3. **Protect matching branches**:
   - ✅ Require a pull request before merging
   - ✅ Require approvals: `1`
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select status checks: `CI`
   - ✅ Do not allow bypassing the above settings

4. Click **Create** or **Save changes**

5. Repeat for the other branch

## Verification

```bash
# Check protection status
gh api repos/:owner/:repo/branches/staging/protection

# Or via web UI
# Navigate to: Settings → Branches
```

## Result

After setup:
- All changes to `staging`/`main` require PRs
- PRs require at least 1 approval
- CI tests must pass before merge
- No force pushes allowed
