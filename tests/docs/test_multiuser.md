# Multi-User Testing Guide

## Objective

Verify that multiple users can use the system simultaneously with complete session isolation. Each user should only see and access their own presentations and jobs.

## Test Setup

You will need:
- **2+ different Google accounts** (e.g., personal and work accounts)
- **2+ browser instances** (use different browsers or incognito/private windows)
- **Active internet connection**

### Browser Setup Recommendations

**Option A: Different Browsers**
- Browser 1: Chrome (normal mode)
- Browser 2: Firefox (normal mode)
- Browser 3: Edge (normal mode)

**Option B: Incognito/Private Windows**
- Browser 1: Chrome (normal mode)
- Browser 2: Chrome (incognito mode)
- Browser 3: Chrome (another incognito mode)

**Note:** Each incognito window is a separate session.

---

## Test Phase 1: Simultaneous Login

### Test 1.1: Two Users Login Simultaneously

**Steps:**
1. **Browser 1**: Navigate to `http://localhost:5000`
2. **Browser 1**: Sign in with Google Account A (e.g., user.a@gmail.com)
3. **Browser 2**: Navigate to `http://localhost:5000`
4. **Browser 2**: Sign in with Google Account B (e.g., user.b@gmail.com)

**Expected Result:**
- ✅ Browser 1 shows: `👤 user.a@gmail.com` in navigation
- ✅ Browser 2 shows: `👤 user.b@gmail.com` in navigation
- ✅ Both users can access the home page simultaneously
- ✅ No conflicts or errors

**Status:** [ ] Pass [ ] Fail

**Notes:**
_________________________________________________________

---

### Test 1.2: Session Isolation Verification

**Steps:**
1. **Browser 1 (User A)**: Note the session (check cookies in dev tools if needed)
2. **Browser 2 (User B)**: Note the session
3. Compare session IDs

**Expected Result:**
- ✅ Different `session_id` values
- ✅ Different `credentials` in each session
- ✅ No credential leakage between sessions

**Status:** [ ] Pass [ ] Fail

---

## Test Phase 2: Job Ownership

### Test 2.1: User A Creates a Job

**Steps:**
1. **Browser 1 (User A)**: Enter a Google Slides URL from User A's account
2. **Browser 1**: Click "📝 Открыть редактор"
3. **Browser 1**: Wait for extraction to complete
4. **Browser 1**: Note the `job_id` from URL (e.g., `/slide_editor?job_id=abc123`)

**Expected Result:**
- ✅ Extraction successful
- ✅ Slides loaded in editor
- ✅ Job created and linked to User A's session

**Test Data:**
- User A's Google Slides URL: ___________________________
- Job ID created: ___________________________

**Status:** [ ] Pass [ ] Fail

---

### Test 2.2: User B Creates a Different Job

**Steps:**
1. **Browser 2 (User B)**: Enter a Google Slides URL from User B's account
2. **Browser 2**: Click "📝 Открыть редактор"
3. **Browser 2**: Wait for extraction to complete
4. **Browser 2**: Note the `job_id` from URL

**Expected Result:**
- ✅ Extraction successful
- ✅ Slides loaded in editor
- ✅ Job created and linked to User B's session
- ✅ Different `job_id` than User A's job

**Test Data:**
- User B's Google Slides URL: ___________________________
- Job ID created: ___________________________

**Status:** [ ] Pass [ ] Fail

---

### Test 2.3: Cross-User Job Access Attempt (CRITICAL)

**Steps:**
1. **Browser 2 (User B)**: Copy User A's job URL from Test 2.1
2. **Browser 2**: Navigate to User A's job URL
   - Example: `http://localhost:5000/slide_editor?job_id=abc123`
3. Observe result

**Expected Result (Current Implementation):**
- ✅ Job loads (jobs are currently accessible across users)
- **Note:** This is expected in current implementation
- **Future Enhancement:** Should show "Access Denied" or "Job Not Found"

**Status:** [ ] Pass (as expected) [ ] Fail

**Notes:**
If you want to implement strict access control, you would need to add:
```python
# In route handlers, check session ownership
if job.get('session_id') != get_session_id():
    return "Access Denied", 403
```

---

### Test 2.4: History Page Isolation (Future Enhancement)

**Steps:**
1. **Browser 1 (User A)**: Navigate to `/history`
2. **Browser 2 (User B)**: Navigate to `/history`
3. Compare the jobs listed

**Expected Result (Current Implementation):**
- ⚠️ Both users see all jobs (no filtering)
- **Future Enhancement:** Each user should only see their own jobs

**Status:** [ ] Pass (current behavior) [ ] Needs filtering

**Recommendation:**
Update `list_all_jobs()` to filter by `session_id`:
```python
def list_all_jobs(limit=50, offset=0, session_id=None):
    # Add WHERE session_id = ? clause
```

---

## Test Phase 3: Credential Isolation

### Test 3.1: User A Accesses Own Google Slides

**Steps:**
1. **Browser 1 (User A)**: Process a presentation from User A's Google account
2. Verify it works

**Expected Result:**
- ✅ Successful access to User A's presentations
- ✅ No authentication errors

**Status:** [ ] Pass [ ] Fail

---

### Test 3.2: User B Accesses Own Google Slides

**Steps:**
1. **Browser 2 (User B)**: Process a presentation from User B's Google account
2. Verify it works

**Expected Result:**
- ✅ Successful access to User B's presentations
- ✅ No authentication errors
- ✅ No interference with User A's session

**Status:** [ ] Pass [ ] Fail

---

### Test 3.3: Verify No Cross-Account Access

**Steps:**
1. **Browser 1 (User A)**: Try to process a presentation that ONLY User B has access to
2. Observe result

**Expected Result:**
- ✅ Error message (Google API returns 403 or 404)
- ✅ User A cannot access User B's private presentations
- ✅ System correctly uses User A's credentials

**Status:** [ ] Pass [ ] Fail

---

## Test Phase 4: Concurrent Operations

### Test 4.1: Simultaneous Presentation Processing

**Steps:**
1. **Browser 1 (User A)**: Start processing a presentation
2. **Browser 2 (User B)**: Immediately start processing a different presentation
3. Monitor both extractions

**Expected Result:**
- ✅ Both extractions proceed simultaneously
- ✅ No conflicts or errors
- ✅ Each extraction uses the correct user's credentials
- ✅ Both complete successfully

**Status:** [ ] Pass [ ] Fail

**Performance Notes:**
- User A extraction time: _______ seconds
- User B extraction time: _______ seconds

---

### Test 4.2: Simultaneous Editing

**Steps:**
1. **Browser 1 (User A)**: Open slide editor for User A's job
2. **Browser 2 (User B)**: Open slide editor for User B's job
3. Make edits in both browsers simultaneously
4. Save changes in both

**Expected Result:**
- ✅ Both editors work independently
- ✅ No interference between sessions
- ✅ Changes saved correctly for each user

**Status:** [ ] Pass [ ] Fail

---

## Test Phase 5: Logout and Session Cleanup

### Test 5.1: User A Logout (While User B Still Logged In)

**Steps:**
1. **Browser 1 (User A)**: Click "Logout"
2. **Browser 2 (User B)**: Verify still logged in

**Expected Result:**
- ✅ Browser 1 redirected to `/login`
- ✅ User A's session cleared
- ✅ Browser 2 (User B) unaffected
- ✅ User B still logged in and functional

**Status:** [ ] Pass [ ] Fail

---

### Test 5.2: User A Re-login (While User B Still Logged In)

**Steps:**
1. **Browser 1**: Sign in with User A again
2. **Browser 2**: Verify User B still logged in

**Expected Result:**
- ✅ User A successfully re-authenticates
- ✅ User A gets a NEW session_id
- ✅ User B's session unaffected
- ✅ Both users can work simultaneously again

**Status:** [ ] Pass [ ] Fail

---

### Test 5.3: All Users Logout

**Steps:**
1. **Browser 1 (User A)**: Logout
2. **Browser 2 (User B)**: Logout
3. **Browser 3 (if used)**: Logout

**Expected Result:**
- ✅ All sessions cleared
- ✅ All browsers show login page
- ✅ No residual session data

**Status:** [ ] Pass [ ] Fail

---

## Test Phase 6: Database Verification

### Test 6.1: Check User Sessions Table

**Steps:**
1. Open database: `db/presentation_jobs.db`
2. Query: `SELECT session_id, user_email, created_at FROM user_sessions;`

**Expected Result:**
- ✅ See entries for both User A and User B
- ✅ Different `session_id` for each
- ✅ Correct `user_email` for each

**SQL Output:**
```
session_id                           | user_email          | created_at
-------------------------------------|---------------------|--------------------
___________________________________  | user.a@gmail.com    | 2025-12-07 ...
___________________________________  | user.b@gmail.com    | 2025-12-07 ...
```

**Status:** [ ] Pass [ ] Fail

---

### Test 6.2: Check Jobs Linked to Sessions

**Steps:**
1. Query: `SELECT id, session_id, presentation_url FROM jobs ORDER BY created_at DESC LIMIT 10;`

**Expected Result:**
- ✅ Jobs have `session_id` populated
- ✅ Jobs created by User A have User A's session_id
- ✅ Jobs created by User B have User B's session_id

**Status:** [ ] Pass [ ] Fail

---

## Test Results Summary

| Test Category | Tests Passed | Tests Failed | Notes |
|---------------|--------------|--------------|-------|
| Simultaneous Login | __ / 2 | __ | |
| Job Ownership | __ / 4 | __ | |
| Credential Isolation | __ / 3 | __ | |
| Concurrent Operations | __ / 2 | __ | |
| Logout & Cleanup | __ / 3 | __ | |
| Database Verification | __ / 2 | __ | |
| **TOTAL** | **__ / 16** | **__** | |

---

## Known Limitations (As Designed)

1. **Job Access**: Jobs are currently accessible by any authenticated user if they know the job_id
   - **Mitigation**: Job IDs are random UUIDs (hard to guess)
   - **Future**: Add session_id validation in routes

2. **History Filtering**: `/history` shows all jobs regardless of session
   - **Future**: Filter by `session_id`

3. **Session Timeout**: 24-hour timeout (configurable)
   - **Current**: Users need to re-login after 24 hours
   - **Future**: Configurable timeout per user type

---

## Recommended Enhancements

### High Priority
- [ ] Add `session_id` validation in job access routes
- [ ] Filter `/history` by session_id
- [ ] Add "Access Denied" error page

### Medium Priority
- [ ] Admin panel to view all sessions
- [ ] Session revocation capability
- [ ] Audit log for cross-session access attempts

### Low Priority
- [ ] User profile page
- [ ] Session management UI
- [ ] Multi-device session tracking

---

## Security Checklist

- [ ] Users cannot access other users' credentials
- [ ] Users cannot modify other users' sessions
- [ ] Session cookies are httpOnly
- [ ] CSRF protection active (OAuth state parameter)
- [ ] Credentials encrypted in database
- [ ] Logout properly clears session
- [ ] Token refresh works transparently
- [ ] No credential exposure in logs

---

## Sign-off

**Tester Name:** _________________________

**Test Date:** _________________________

**Browsers Used:**
1. _________________________
2. _________________________
3. _________________________

**Google Accounts Used:**
1. _________________________ (User A)
2. _________________________ (User B)

**Overall Result:** [ ] All Pass [ ] Some Failed [ ] Needs Enhancement

**Critical Issues Found:**
_________________________________________________________
_________________________________________________________

**Recommendations:**
_________________________________________________________
_________________________________________________________
