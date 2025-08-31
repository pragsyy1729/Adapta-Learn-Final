import threading
import time
import uuid
from queue import Queue, Empty
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import os
import json

class JobStatus:
    """Enum-like class for job statuses."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingJob:
    """Represents a document processing job."""
    def __init__(self, job_id: str, department_id: str, filename: str, user_id: str = None):
        self.job_id = job_id
        self.department_id = department_id
        self.filename = filename
        self.user_id = user_id
        self.status = JobStatus.PENDING
        self.progress = 0
        self.current_step = ""
        self.total_steps = 6  # Based on document processing pipeline
        self.completed_steps = 0
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.elapsed_time = 0
        self.error_message = None
        self.processing_details = {
            "total_chunks": 0,
            "processed_chunks": 0,
            "concepts_extracted": 0,
            "embeddings_created": 0
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for API responses."""
        return {
            "job_id": self.job_id,
            "department_id": self.department_id,
            "filename": self.filename,
            "user_id": self.user_id,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "elapsed_time": self.elapsed_time,
            "error_message": self.error_message,
            "processing_details": self.processing_details
        }

    def update_progress(self, step: str, progress: int = None):
        """Update job progress."""
        self.current_step = step
        if progress is not None:
            self.progress = progress
        self.completed_steps = min(self.total_steps, self.completed_steps + 1)

        if self.started_at:
            self.elapsed_time = (datetime.now() - self.started_at).total_seconds()

class JobQueue:
    """Simple in-memory job queue for document processing."""

    def __init__(self):
        self.jobs: Dict[str, ProcessingJob] = {}
        self.job_queue = Queue()
        self.worker_thread = None
        self.running = False
        self.lock = threading.Lock()

        # Start the worker thread
        self.start_worker()

    def start_worker(self):
        """Start the background worker thread."""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            print("📋 Job queue worker started")

    def stop_worker(self):
        """Stop the background worker thread."""
        print("🛑 Stopping job queue worker...")
        self.running = False
        if self.worker_thread and self.worker_thread.is_alive():
            # Give the worker thread a moment to finish gracefully
            self.worker_thread.join(timeout=5)
            if self.worker_thread.is_alive():
                print("⚠️  Worker thread did not stop gracefully")
            else:
                print("📋 Job queue worker stopped gracefully")

    def _worker_loop(self):
        """Main worker loop that processes jobs from the queue."""
        while self.running:
            try:
                # Get job from queue with timeout
                job_data = self.job_queue.get(timeout=1)

                if job_data:
                    self._process_job(job_data)
                    self.job_queue.task_done()

            except Empty:
                # Queue is empty, continue the loop to check self.running
                continue
            except Exception as e:
                print(f"❌ Error in job worker loop: {e}")
                time.sleep(1)  # Brief pause before retrying

    def _process_job(self, job_data: Dict[str, Any]):
        """Process a single job."""
        job_id = job_data['job_id']
        job = self.jobs.get(job_id)

        if not job:
            print(f"⚠️  Job {job_id} not found in jobs dict")
            return

        try:
            # Update job status
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.now()
            job.update_progress("Initializing document processing", 10)

            # Import document processor here to avoid circular imports
            try:
                from .document_processor import document_processor
            except ImportError as e:
                raise Exception(f"Failed to import document processor: {e}")

            # Step 1: Extract text
            job.update_progress("Extracting text from document", 20)
            text = self._extract_text_from_file(job_data['file_path'])
            if not text.strip():
                raise Exception("No text could be extracted from the document")
            job.processing_details["total_chunks"] = max(1, len(text) // 1000)  # Estimate chunks
            time.sleep(0.5)

            # Step 2: Process chunks
            job.update_progress("Chunking text into segments", 40)
            chunks = self._chunk_text(text)
            job.processing_details["total_chunks"] = len(chunks)
            job.processing_details["processed_chunks"] = len(chunks)
            time.sleep(0.5)

            # Step 3: Extract concepts
            job.update_progress("Extracting key concepts", 60)
            concepts = self._extract_concepts(text)
            job.processing_details["concepts_extracted"] = len(concepts)
            time.sleep(0.5)

            # Step 4: Create knowledge graph
            job.update_progress("Creating knowledge graph", 80)
            knowledge_graph = self._create_knowledge_graph(chunks, concepts)
            time.sleep(0.5)

            # Step 5: Generate embeddings and update vector store
            job.update_progress("Generating embeddings and updating vector store", 90)

            # Actually process the document
            result = document_processor.process_document(
                file_path=job_data['file_path'],
                department_id=job.department_id,
                metadata={
                    'filename': job.filename,
                    'uploaded_by': job.user_id or 'anonymous',
                    'job_id': job_id
                }
            )

            if result.get("success", False):
                job.status = JobStatus.COMPLETED
                job.progress = 100
                job.completed_at = datetime.now()
                job.update_progress("Document processing completed successfully", 100)

                # Update processing details with actual data from document processor
                job.processing_details = {
                    "total_chunks": result.get("total_chunks", 0),
                    "processed_chunks": result.get("total_chunks", 0),
                    "concepts_extracted": result.get("concepts_extracted", 0),
                    "embeddings_created": result.get("documents_created", 0)
                }

                # Add the processed document to department's documentation
                self._add_processed_document_to_department(
                    department_id=job.department_id,
                    document_name=job.filename,
                    file_path=job_data['file_path']
                )

                print(f"✅ Job {job_id} completed successfully")
            else:
                raise Exception(result.get("error", "Document processing failed"))

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
            print(f"❌ Job {job_id} failed: {e}")

    def _add_processed_document_to_department(self, department_id: str, document_name: str, file_path: str):
        """Add a processed document to the department's documentation list."""
        try:
            # Extract text from the file
            document_content = self._extract_text_from_file(file_path)
            
            if not document_content.strip():
                print(f"⚠️  No text content extracted from {document_name}")
                return
            
            # Truncate content if too long for UI display
            if len(document_content) > 5000:
                document_content = document_content[:5000] + "...\n\n[Content truncated for display]"
            
            # Use data_access service to get the correct path
            try:
                from ..services.data_access import get_data_file_path
                departments_file = get_data_file_path('department.json')
            except ImportError:
                # Fallback to direct path construction
                import os
                # Get the project root directory (adapta-learn folder)
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
                departments_file = os.path.join(project_root, 'data', 'department.json')
            
            print(f"📁 Looking for departments file at: {departments_file}")
            
            try:
                with open(departments_file, 'r', encoding='utf-8') as f:
                    departments_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"⚠️  Could not load departments file: {departments_file} - {e}")
                return
            
            departments = departments_data.get("departments", [])
            print(f"📋 Found {len(departments)} departments")
            
            # Find the department and add/update documentation
            for dept in departments:
                if dept.get("id") == department_id:
                    print(f"✅ Found department {department_id}")
                    if "documentation" not in dept or not isinstance(dept["documentation"], list):
                        dept["documentation"] = []
                        print(f"📝 Created documentation array for department {department_id}")
                    
                    # Check if document with same name already exists
                    existing_doc = None
                    for doc in dept["documentation"]:
                        if doc.get("name") == document_name:
                            existing_doc = doc
                            break
                    
                    if existing_doc:
                        # Update existing document
                        existing_doc["document_content"] = document_content
                        print(f"📝 Updated existing document: {document_name}")
                    else:
                        # Add new document
                        dept["documentation"].append({
                            "name": document_name,
                            "document_content": document_content
                        })
                        print(f"📄 Added new document: {document_name}")
                    
                    # Save updated departments data
                    with open(departments_file, 'w', encoding='utf-8') as f:
                        json.dump(departments_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"✅ Document {document_name} added to department {department_id} documentation")
                    return
            
            print(f"⚠️  Department {department_id} not found in departments data")
            
        except Exception as e:
            print(f"❌ Error adding processed document to department: {e}")
            import traceback
            traceback.print_exc()

    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from various file types."""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return self._extract_text_from_pdf(file_path)
            elif file_extension in ['.docx', '.doc']:
                return self._extract_text_from_docx(file_path)
            elif file_extension == '.txt':
                return self._extract_text_from_txt(file_path)
            else:
                print(f"⚠️  Unsupported file type for text extraction: {file_extension}")
                return ""
                
        except Exception as e:
            print(f"❌ Error extracting text from {file_path}: {e}")
            return ""

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            print("⚠️  PyPDF2 not available for PDF text extraction")
            return ""
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {e}")
            return ""

    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            import docx
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            print("⚠️  python-docx not available for DOCX text extraction")
            return ""
        except Exception as e:
            print(f"❌ Error extracting text from DOCX: {e}")
            return ""

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks for processing."""
        # Simple chunking - split by paragraphs, then by sentences
        chunks = []
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if len(para.strip()) > 1000:
                # Split long paragraphs into sentences
                sentences = para.split('. ')
                current_chunk = ""
                
                for sentence in sentences:
                    if len(current_chunk + sentence) > 800:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        current_chunk += ". " + sentence if current_chunk else sentence
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
            elif para.strip():
                chunks.append(para.strip())
        
        return chunks if chunks else [text[:1000]]

    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text (simplified version)."""
        # Simple extraction based on capitalization and common patterns
        import re
        words = re.findall(r'\b[A-Z][a-z]+\b', text[:2000])
        # Filter out common words and get unique concepts
        common_words = {'The', 'And', 'For', 'Are', 'But', 'Not', 'You', 'All', 'Can', 'Had', 'Her', 'Was', 'One', 'Our', 'Out', 'Day', 'Get', 'Has', 'Him', 'His', 'How', 'Its', 'May', 'New', 'Now', 'Old', 'See', 'Two', 'Who', 'Boy', 'Did', 'She', 'Use', 'Way', 'Why'}
        concepts = [word for word in words if word not in common_words and len(word) > 3]
        return list(set(concepts))[:10]  # Return up to 10 unique concepts

    def _create_knowledge_graph(self, chunks: List[str], concepts: List[str]) -> Dict[str, Any]:
        """Create a simple knowledge graph structure."""
        return {
            "nodes": [{"id": f"concept_{i}", "label": concept} for i, concept in enumerate(concepts)],
            "relationships": [],
            "chunks": chunks
        }

    def submit_job(self, department_id: str, filename: str, file_path: str, user_id: str = None) -> str:
        """Submit a new processing job."""
        job_id = str(uuid.uuid4())

        with self.lock:
            job = ProcessingJob(job_id, department_id, filename, user_id)
            self.jobs[job_id] = job

            # Add to processing queue
            job_data = {
                'job_id': job_id,
                'file_path': file_path,
                'department_id': department_id
            }
            self.job_queue.put(job_data)

        print(f"📋 Submitted job {job_id} for department {department_id}, file: {filename}")
        return job_id

    def get_job(self, job_id: str) -> Optional[ProcessingJob]:
        """Get a job by ID."""
        with self.lock:
            return self.jobs.get(job_id)

    def get_department_jobs(self, department_id: str) -> list:
        """Get all jobs for a department."""
        with self.lock:
            return [
                job for job in self.jobs.values()
                if job.department_id == department_id
            ]

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Clean up old completed/failed jobs."""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

        with self.lock:
            jobs_to_remove = []
            for job_id, job in self.jobs.items():
                if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                    if job.completed_at and job.completed_at.timestamp() < cutoff_time:
                        jobs_to_remove.append(job_id)

            for job_id in jobs_to_remove:
                del self.jobs[job_id]
                print(f"🗑️  Cleaned up old job: {job_id}")

# Global job queue instance
job_queue = JobQueue()
