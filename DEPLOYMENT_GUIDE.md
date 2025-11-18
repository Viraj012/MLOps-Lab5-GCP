# 🚀 Lab 5 Deployment Guide - Step by Step

## ✅ FILES READY:
- main.py (with Pipeline Metadata Logging feature added)
- schemas.yaml (includes pipeline_logs table)
- requirements.txt
- table_1_test.json (test data file)

---

## 📋 YOUR ACTION ITEMS (GCP Console - ~15 mins)

### PHASE 1: GCP SETUP (5 minutes)

#### Step 1: Enable Cloud Functions API
1. Open Google Cloud Console: https://console.cloud.google.com
2. Click on Navigation Menu (☰) → APIs & Services → Library
3. In the search bar, type: "Cloud Functions API"
4. Click on it and click the blue "ENABLE" button
5. Wait for it to enable (~30 seconds)

#### Step 2: Create Google Cloud Storage Bucket
1. In GCP Console, click Navigation Menu (☰) → Cloud Storage → Buckets
2. Click "CREATE BUCKET" button (blue button at top)
3. Fill in:
   - Bucket name: `viraj-mlops-etl-lab5` (must be globally unique, add numbers if taken)
   - Location type: Select "Region"
   - Region: Select "us-central1" ⚠️ IMPORTANT: Remember this region!
4. Leave everything else as default
5. Click "CREATE"

#### Step 3: Create BigQuery Dataset
1. In GCP Console, click Navigation Menu (☰) → BigQuery
2. In the BigQuery console, find your project name in the left sidebar
3. Click the three dots (⋮) next to your project name
4. Click "Create dataset"
5. Fill in:
   - Dataset ID: `staging` ⚠️ CRITICAL: Must be exactly "staging"
   - Location: us-central1 (same as bucket)
6. Click "CREATE DATASET"

#### Step 4: Set Up IAM Permissions
1. Click Navigation Menu (☰) → IAM & Admin → IAM
2. Look for the service account that looks like:
   `PROJECT_NUMBER-compute@developer.gserviceaccount.com`
   (It's usually near the top, has "Compute Engine default service account" in description)
3. Click the pencil/edit icon (✏️) on the right side of that row
4. Click "+ ADD ANOTHER ROLE"
5. In the search box, type "BigQuery Admin" and select it
6. Click "+ ADD ANOTHER ROLE" again
7. In the search box, type "Eventarc Event Receiver" and select it
8. Click "SAVE"

---

### PHASE 2: DEPLOY CLOUD FUNCTION (5 minutes)

#### Step 5: Create Cloud Function
1. Click Navigation Menu (☰) → Cloud Run functions
2. Click "CREATE FUNCTION" (blue button at top)
3. Fill in Configuration:

   **Environment:** 2nd gen (should be selected by default)
   
   **Function name:** `viraj-etl-function`
   
   **Region:** `us-central1` ⚠️ MUST MATCH YOUR BUCKET REGION
   
4. Under "Trigger":
   - Trigger type: Click "Cloud Storage"
   - Event type: Select "google.cloud.storage.object.v1.finalized"
   - Cloud Storage bucket: Click "BROWSE" and select your bucket (`viraj-mlops-etl-lab5`)
   
5. Click "NEXT" (blue button at bottom)

#### Step 6: Upload Code Files
1. In the "Code" section:
   - Runtime: Select "Python 3.11"
   - Entry point: Type exactly `hello_gcs`
   
2. You'll see inline editor with main.py already there
   
3. For each file, do this:
   
   **For main.py:**
   - Click on "main.py" in the file list on left
   - Delete all existing code (Ctrl+A, then Delete)
   - Open the main.py file from your Lab-5 folder
   - Copy ALL the code (Ctrl+A, Ctrl+C)
   - Paste into the editor (Ctrl+V)
   
   **For requirements.txt:**
   - Click on "requirements.txt" in the file list on left
   - Delete all existing content
   - Open the requirements.txt file from your Lab-5 folder
   - Copy and paste the content
   
   **Add schemas.yaml:**
   - Click "+ ADD FILE" at the top of file list
   - Name it: `schemas.yaml`
   - Open the schemas.yaml file from your Lab-5 folder
   - Copy ALL the content and paste it

4. Double-check entry point still shows: `hello_gcs`

5. Click "DEPLOY" (blue button at bottom)

6. ⏳ WAIT: Deployment takes 2-4 minutes. You'll see a spinner next to the function name.
   Wait until you see a green checkmark ✓

---

### PHASE 3: TEST THE PIPELINE (5 minutes)

#### Step 7: Upload Test Data
1. Go to Navigation Menu (☰) → Cloud Storage → Buckets
2. Click on your bucket name (`viraj-mlops-etl-lab5`)
3. Click "UPLOAD FILES" button
4. Select the file: `table_1_test.json` from your Lab-5 folder
5. Click "Upload"
6. ⚡ The Cloud Function triggers automatically!

#### Step 8: Check Function Logs
1. Go to Navigation Menu (☰) → Cloud Run functions
2. Click on your function name (`viraj-etl-function`)
3. Click on "LOGS" tab at the top
4. You should see logs showing:
   - "Bucket name: viraj-mlops-etl-lab5"
   - "File name: table_1_test.json"
   - "Created table..." or table already exists
   - "Job finished."
   - "Pipeline metadata logged successfully"
   
📸 **SCREENSHOT 1: Take screenshot of these logs!**

#### Step 9: Verify Data in BigQuery
1. Go to Navigation Menu (☰) → BigQuery
2. In the left sidebar, expand your project → expand `staging` dataset
3. You should see TWO tables:
   - `table_1` (your data table)
   - `pipeline_logs` (our custom enhancement! ✨)
   
4. Click on `table_1`
5. Click "QUERY" → "In new tab"
6. Run this query:
   ```sql
   SELECT * FROM `staging.table_1` LIMIT 10
   ```
7. You should see 3 rows of data (Viraj, John, Jane)

📸 **SCREENSHOT 2: Take screenshot of query results!**

8. Now query the pipeline_logs table:
   ```sql
   SELECT * FROM `staging.pipeline_logs` ORDER BY timestamp DESC LIMIT 10
   ```
9. You should see 1 row showing:
   - pipeline_run_id (UUID)
   - timestamp
   - file_name: table_1_test.json
   - status: SUCCESS
   - processing_time_seconds
   
📸 **SCREENSHOT 3: Take screenshot of pipeline_logs results!**

---

## 🎯 WHAT MAKES THIS SPECIAL (Your Custom Enhancement)

The **pipeline_logs** table is YOUR custom addition that provides:
- ✅ Complete observability of all pipeline runs
- ✅ Success/failure tracking
- ✅ Performance monitoring (processing time)
- ✅ Error tracking for debugging
- ✅ Audit trail for compliance

This demonstrates MLOps best practices for monitoring and observability!

---

## 📸 REQUIRED SCREENSHOTS FOR SUBMISSION:
1. Cloud Function logs showing successful execution
2. BigQuery `table_1` with your test data
3. BigQuery `pipeline_logs` showing metadata tracking (YOUR CUSTOM FEATURE!)
4. (Optional) GCS bucket with uploaded file

---

## 🔥 BONUS: Test Failure Scenario (Optional)
Want to see the error logging in action?

1. Upload a badly formatted JSON file to your bucket
2. Check pipeline_logs - you'll see status: "FAILED" with error details!

---

## ✅ YOU'RE DONE!
Total time: ~15-20 minutes
Custom enhancement: Pipeline Metadata Logging ✨

Questions? Check the logs first, they're super helpful!