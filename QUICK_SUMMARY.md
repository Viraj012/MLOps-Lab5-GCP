# Lab 5 - Quick Summary

## What We Built:
Automated ETL Pipeline: Google Cloud Storage → BigQuery using Cloud Functions

## Custom Enhancement Added:
**Pipeline Metadata Logging System** 
- Automatically tracks every pipeline run
- Logs: timestamp, file name, status, processing time, errors
- Stored in `staging.pipeline_logs` table in BigQuery
- Provides observability and monitoring for MLOps best practices

## Files Ready to Deploy:
1. ✅ main.py - Enhanced with metadata logging
2. ✅ schemas.yaml - Includes pipeline_logs table schema
3. ✅ requirements.txt - All dependencies
4. ✅ table_1_test.json - Sample test data

## What You Need to Do:
Follow the step-by-step guide in: **DEPLOYMENT_GUIDE.md**

Time Required: ~15 minutes

## Expected Results:
1. Cloud Function deploys successfully
2. Upload JSON file triggers function automatically
3. Data appears in BigQuery `staging.table_1`
4. Metadata appears in BigQuery `staging.pipeline_logs` (YOUR ENHANCEMENT!)
5. All logs show success

## Screenshots Needed:
1. Cloud Function logs
2. BigQuery table_1 query results  
3. BigQuery pipeline_logs query results (shows your custom feature!)

Good luck! 🚀