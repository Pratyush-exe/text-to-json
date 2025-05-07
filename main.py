import time
import streamlit as st
import json
import os
from pathlib import Path
import concurrent.futures
import uuid
from datetime import datetime
from t2j.workflow import Workflow  


# Initialize session state
if 'pdf_files' not in st.session_state:
    st.session_state.pdf_files = []
if 'json_data' not in st.session_state:
    st.session_state.json_data = None
if 'pdf_paths' not in st.session_state:
    st.session_state.pdf_paths = []
if 'json_path' not in st.session_state:
    st.session_state.json_path = None
if 'workflow_results' not in st.session_state:
    st.session_state.workflow_results = {}
if 'active_workflows' not in st.session_state:
    st.session_state.active_workflows = {}
if 'log_positions' not in st.session_state:
    st.session_state.log_positions = {} 

st.title("File Upload and Processor")

# File uploaders
st.header("Upload PDF Files")
uploaded_pdfs = st.file_uploader(
    "Choose PDF files", 
    type="pdf", 
    accept_multiple_files=True,
    key="pdf_uploader"
)

st.header("Upload JSON File")
uploaded_json = st.file_uploader(
    "Choose a JSON file", 
    type="json",
    key="json_uploader"
)

if uploaded_pdfs:
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    pdf_paths = []
    for uploaded_pdf in uploaded_pdfs:
        file_path = temp_dir / f"{uuid.uuid4().hex}_{uploaded_pdf.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        pdf_paths.append(str(file_path))
    
    st.session_state.pdf_paths = pdf_paths
else:
    st.session_state.pdf_paths = []

if uploaded_json:
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    json_path = temp_dir / f"{uuid.uuid4().hex}_{uploaded_json.name}"
    with open(json_path, "wb") as f:
        f.write(uploaded_json.getbuffer())
    
    st.session_state.json_path = str(json_path)
else:
    st.session_state.json_path = None
    
def run_workflow(pdf_path, json_path, trace_id):
    try:
        workflow = Workflow(trace_id)
        result = workflow.run(pdf_path, json_path)
        
        return {
            'status': 'completed',
            'result': result,
            'pdf_path': pdf_path,
            'trace_id': trace_id,
            'workflow': workflow
        }
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'pdf_path': pdf_path,
            'trace_id': trace_id,
            'workflow': workflow if 'workflow' in locals() else None
        }

if st.button("Process Files"):
    if st.session_state.pdf_paths and st.session_state.json_path:
        st.json(open(st.session_state.json_path, "r").read())
        
        st.session_state.workflow_results = {}
        st.session_state.active_workflows = {}
        st.session_state.log_positions = {}
        
        logs_placeholder = st.empty()
        
        # Run workflows in parallel
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     futures = {}
        #     for pdf_path in st.session_state.pdf_paths:
        #         trace_id = str(uuid.uuid4())
        #         future = executor.submit(
        #             run_workflow,
        #             pdf_path,
        #             st.session_state.json_path,
        #             trace_id
        #         )
        #         futures[future] = trace_id
        #         st.session_state.active_workflows[trace_id] = {
        #             'pdf_path': pdf_path,
        #             'status': 'running',
        #             'start_time': datetime.now(),
        #             'workflow': None  # Will be populated when workflow starts
        #         }
        #         st.session_state.log_positions[trace_id] = 0  # Initial log position
            
        #     # Monitor progress and update UI in real-time
        #     while futures:
        #         # Check for completed futures
        #         done, _ = concurrent.futures.wait(futures, timeout=0.1, return_when=concurrent.futures.FIRST_COMPLETED)
                
        #         for future in done:
        #             trace_id = futures.pop(future)
        #             result = future.result()
                    
        #             # Update session state with results
        #             st.session_state.workflow_results[trace_id] = result
        #             st.session_state.active_workflows[trace_id]['status'] = result['status']
        #             st.session_state.active_workflows[trace_id]['end_time'] = datetime.now()
        #             st.session_state.active_workflows[trace_id]['workflow'] = result.get('workflow')
                
        #         # Update the live logs display
        #         with logs_placeholder.container():
        #             st.subheader("Workflow Execution Progress")
                    
        #             for trace_id, workflow_info in st.session_state.active_workflows.items():
        #                 expander_key = f"expander_{trace_id}"
        #                 status = workflow_info['status']
                        
        #                 with st.expander(f"Workflow {trace_id} - {os.path.basename(workflow_info['pdf_path'])} - {status.upper()}"):
        #                     if status == 'completed':
        #                         result = st.session_state.workflow_results[trace_id]
        #                         st.success(f"Completed in {(workflow_info['end_time'] - workflow_info['start_time']).total_seconds():.2f} seconds")
                                
        #                         # Read all logs at completion
        #                         if result.get('workflow'):
        #                             logs, _ = result['workflow'].get_latest_logs(0)
        #                             st.write(logs, height=200)
        #                         st.json(result.get('result', {}))
                            
        #                     elif status == 'failed':
        #                         result = st.session_state.workflow_results[trace_id]
        #                         st.error(f"Failed after {(datetime.now() - workflow_info['start_time']).total_seconds():.2f} seconds")
        #                         st.write(result.get('error', 'Unknown error'), height=100)
                                
        #                         # Read all logs at failure
        #                         if result.get('workflow'):
        #                             logs, _ = result['workflow'].get_latest_logs(0)
        #                             st.write(logs, height=200)
                            
        #                     else:  # running
        #                         st.info(f"Running for {(datetime.now() - workflow_info['start_time']).total_seconds():.2f} seconds...")
                                
        #                         # Get latest logs for running workflows
        #                         if workflow_info.get('workflow'):
        #                             logs, new_pos = workflow_info['workflow'].get_latest_logs(st.session_state.log_positions[trace_id])
        #                             st.session_state.log_positions[trace_id] = new_pos
        #                             st.write(logs, height=200)
        #                         else:
        #                             st.info("Workflow initializing...")
        #         time.sleep(0.1)
        
        # Run workflows sequentially
        for pdf_path in st.session_state.pdf_paths:
            trace_id = str(uuid.uuid4())
            st.session_state.active_workflows[trace_id] = {
                'pdf_path': pdf_path,
                'status': 'running',
                'start_time': datetime.now(),
                'workflow': None
            }
            st.session_state.log_positions[trace_id] = 0
            
            try:
                result = run_workflow(
                    pdf_path,
                    st.session_state.json_path,
                    trace_id
                )
                
                st.session_state.workflow_results[trace_id] = result
                st.session_state.active_workflows[trace_id]['status'] = result['status']
                st.session_state.active_workflows[trace_id]['end_time'] = datetime.now()
                st.session_state.active_workflows[trace_id]['workflow'] = result.get('workflow')
                
            except Exception as e:
                st.session_state.workflow_results[trace_id] = {
                    'status': 'failed',
                    'error': str(e),
                    'workflow': st.session_state.active_workflows[trace_id].get('workflow')
                }
                st.session_state.active_workflows[trace_id]['status'] = 'failed'
                st.session_state.active_workflows[trace_id]['end_time'] = datetime.now()
            
            with logs_placeholder.container():
                st.subheader("Workflow Execution Progress")
                
                for trace_id, workflow_info in st.session_state.active_workflows.items():
                    expander_key = f"expander_{trace_id}"
                    status = workflow_info['status']
                    
                    with st.expander(f"Workflow {trace_id} - {os.path.basename(workflow_info['pdf_path'])} - {status.upper()}"):
                        if status == 'completed':
                            result = st.session_state.workflow_results[trace_id]
                            st.success(f"Completed in {(workflow_info['end_time'] - workflow_info['start_time']).total_seconds():.2f} seconds")
                            
                            # Read all logs at completion
                            # if result.get('workflow'):
                            #     logs, _ = result['workflow'].get_latest_logs(0)
                            #     st.write(logs, height=200)
                            st.json(result.get('result', {}))
                        
                        elif status == 'failed':
                            result = st.session_state.workflow_results[trace_id]
                            st.error(f"Failed after {(datetime.now() - workflow_info['start_time']).total_seconds():.2f} seconds")
                            # st.write(result.get('error', 'Unknown error'), height=100)
                            
                            # Read all logs at failure
                            # if result.get('workflow'):
                            #     logs, _ = result['workflow'].get_latest_logs(0)
                            #     st.write(logs, height=200)
                        
                        else:
                            st.info(f"Running for {(datetime.now() - workflow_info['start_time']).total_seconds():.2f} seconds...")
                            
                            if workflow_info.get('workflow'):
                                logs, new_pos = workflow_info['workflow'].get_latest_logs(st.session_state.log_positions[trace_id])
                                st.session_state.log_positions[trace_id] = new_pos
                                # st.write(logs, height=200)
                            else:
                                st.info("Workflow initializing...")
        
        st.success("All workflows completed!")
    else:
        st.warning("Please upload both PDF and JSON files first")

if st.session_state.workflow_results:
    final_output = []    
    for key, value in st.session_state.workflow_results.items():
        try:
            final_output.append(value['result'])
        except:
            pass
        
    st.json(final_output)