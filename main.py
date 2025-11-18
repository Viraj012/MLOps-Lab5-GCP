import functions_framework

import logging
import os
import traceback
import re
import time
import uuid
from datetime import datetime

from google.cloud import bigquery
from google.cloud import storage

import yaml

with open("./schemas.yaml") as schema_file:
    config = yaml.load(schema_file, Loader=yaml.Loader)

PROJECT_ID = os.getenv('cloudquicklab')
BQ_DATASET = 'staging'
CS = storage.Client()
BQ = bigquery.Client()
job_config = bigquery.LoadJobConfig()


def streaming(data):
    bucketname = data['bucket']
    print("Bucket name", bucketname)
    filename = data['name']
    print("File name", filename)
    timeCreated = data['timeCreated']
    print("Time Created", timeCreated)
    
    start_time = time.time()
    target_table = None
    
    try:
        for table in config:
            tableName = table.get('name')
            if re.search(tableName.replace('_', '-'), filename) or re.search(tableName, filename):
                target_table = tableName
                tableSchema = table.get('schema')
                _check_if_table_exists(tableName, tableSchema)
                tableFormat = table.get('format')
                if tableFormat == 'NEWLINE_DELIMITED_JSON':
                    _load_table_from_uri(data['bucket'], data['name'], tableSchema, tableName)
                
                processing_time = time.time() - start_time
                
                # Log success
                log_pipeline_metadata(
                    bucket_name=bucketname,
                    file_name=filename,
                    target_table=target_table,
                    status="SUCCESS",
                    rows_loaded=None,  # Could be enhanced to count rows
                    error_message=None,
                    processing_time=processing_time
                )
                
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = traceback.format_exc()
        print('Error streaming file. Cause: %s' % (error_msg))
        
        # Log failure
        log_pipeline_metadata(
            bucket_name=bucketname,
            file_name=filename,
            target_table=target_table,
            status="FAILED",
            rows_loaded=None,
            error_message=str(e),
            processing_time=processing_time
        )


def _check_if_table_exists(tableName, tableSchema):
    table_id = BQ.dataset(BQ_DATASET).table(tableName)

    try:
        BQ.get_table(table_id)
    except Exception:
        logging.warn('Creating table: %s' % (tableName))
        schema = create_schema_from_yaml(tableSchema)
        table = bigquery.Table(table_id, schema=schema)
        table = BQ.create_table(table)
        print("Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id))


def _load_table_from_uri(bucket_name, file_name, tableSchema, tableName):
    uri = 'gs://%s/%s' % (bucket_name, file_name)
    table_id = BQ.dataset(BQ_DATASET).table(tableName)

    schema = create_schema_from_yaml(tableSchema)
    print(schema)
    job_config.schema = schema

    job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    job_config.write_disposition = 'WRITE_APPEND',

    load_job = BQ.load_table_from_uri(
        uri,
        table_id,
        job_config=job_config,
    )

    load_job.result()
    print("Job finished.")


def create_schema_from_yaml(table_schema):
    schema = []
    for column in table_schema:

        schemaField = bigquery.SchemaField(column['name'], column['type'], column['mode'])

        schema.append(schemaField)

        if column['type'] == 'RECORD':
            schemaField._fields = create_schema_from_yaml(column['fields'])
    return schema


def log_pipeline_metadata(bucket_name, file_name, target_table, status, rows_loaded=None, error_message=None, processing_time=None):
    """
    Log pipeline execution metadata to BigQuery for monitoring and observability.
    This is our custom enhancement for the lab.
    """
    try:
        pipeline_run_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        log_entry = {
            "pipeline_run_id": pipeline_run_id,
            "timestamp": timestamp,
            "file_name": file_name,
            "bucket_name": bucket_name,
            "target_table": target_table,
            "status": status,
            "rows_loaded": rows_loaded,
            "error_message": error_message,
            "processing_time_seconds": processing_time
        }
        
        table_id = f"{BQ.project}.{BQ_DATASET}.pipeline_logs"
        
        # Ensure pipeline_logs table exists
        _check_if_table_exists("pipeline_logs", [
            {'name': 'pipeline_run_id', 'type': 'STRING', 'mode': 'REQUIRED'},
            {'name': 'timestamp', 'type': 'TIMESTAMP', 'mode': 'REQUIRED'},
            {'name': 'file_name', 'type': 'STRING', 'mode': 'REQUIRED'},
            {'name': 'bucket_name', 'type': 'STRING', 'mode': 'REQUIRED'},
            {'name': 'target_table', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'status', 'type': 'STRING', 'mode': 'REQUIRED'},
            {'name': 'rows_loaded', 'type': 'INT64', 'mode': 'NULLABLE'},
            {'name': 'error_message', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'processing_time_seconds', 'type': 'FLOAT64', 'mode': 'NULLABLE'}
        ])
        
        # Insert log entry
        errors = BQ.insert_rows_json(table_id, [log_entry])
        if errors:
            print(f"Errors inserting pipeline log: {errors}")
        else:
            print(f"Pipeline metadata logged successfully for run {pipeline_run_id}")
            
    except Exception as e:
        print(f"Failed to log pipeline metadata: {str(e)}")
        # Don't fail the main pipeline if logging fails



@functions_framework.cloud_event
def hello_gcs(cloud_event):
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]

    print(f"Event ID: {event_id}")
    print(f"Event type: {event_type}")
    print(f"Bucket: {bucket}")
    print(f"File: {name}")
    print(f"Metageneration: {metageneration}")
    print(f"Created: {timeCreated}")
    print(f"Updated: {updated}")

    streaming(data)
