import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Document {
  name: string;
  document_content: string;
}

interface ProcessingJob {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  total_steps: number;
  completed_steps: number;
  department_id: string;
  filename: string;
  error_message?: string;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  elapsed_time: number;
  processing_details: {
    total_chunks: number;
    processed_chunks: number;
    concepts_extracted: number;
    embeddings_created: number;
  };
}

interface DepartmentDocsManagerProps {
  departmentId: string;
  departmentName: string;
}

const API_BASE = '/api/admin/departments';

const DepartmentDocsManager: React.FC<DepartmentDocsManagerProps> = ({ departmentId, departmentName }) => {
  const [docs, setDocs] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [form, setForm] = useState<Document>({ name: '', document_content: '' });
  const [saving, setSaving] = useState(false);
  const [processingJobs, setProcessingJobs] = useState<ProcessingJob[]>([]);
  const [currentProcessingId, setCurrentProcessingId] = useState<string | null>(null);

  useEffect(() => {
    fetchDocs();
    fetchProcessingJobs();
    // eslint-disable-next-line
  }, [departmentId]);

  // Poll for processing status updates
  useEffect(() => {
    if (processingJobs.some(job => job.status === 'pending' || job.status === 'processing')) {
      const interval = setInterval(() => {
        fetchProcessingJobs();
        // Also refresh documents when jobs complete
        if (processingJobs.some(job => job.status === 'completed')) {
          fetchDocs();
        }
      }, 2000); // Poll every 2 seconds
      return () => clearInterval(interval);
    }
  }, [processingJobs]);

  const fetchDocs = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_BASE}/${departmentId}/documentation`);
      setDocs(res.data || []);
    } catch (e: any) {
      setError('Failed to load documentation.');
    } finally {
      setLoading(false);
    }
  };

  const fetchProcessingJobs = async () => {
    try {
      const response = await axios.get(`/api/conversation/departments/${departmentId}/processing`);
      setProcessingJobs(response.data.processing_jobs || []);
    } catch (error) {
      console.error('Failed to fetch processing jobs:', error);
    }
  };

  const fetchProcessingStatus = async (processingId: string) => {
    try {
      const response = await axios.get(`/api/conversation/processing/${processingId}/status`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch processing status:', error);
      return null;
    }
  };

  const handleAdd = () => {
    setForm({ name: '', document_content: '' });
    setEditIndex(null);
    setShowForm(true);
  };

  const handleEdit = (idx: number) => {
    setForm(docs[idx]);
    setEditIndex(idx);
    setShowForm(true);
  };

  const handleDelete = async (idx: number) => {
    // For now, just remove from UI and re-upload all docs (since backend does not support DELETE)
    const newDocs = docs.filter((_, i) => i !== idx);
    setDocs(newDocs);
    // Optionally, you can implement a batch update endpoint for full sync
    // For now, just inform the admin to re-add docs as needed
  };


  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Handle file upload using the new conversation agent endpoint
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['application/pdf', 'text/html', 'text/plain'];
    const allowedExtensions = ['.pdf', '.html', '.txt'];

    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    const isValidType = allowedTypes.includes(file.type) || allowedExtensions.includes(fileExtension);

    if (!isValidType) {
      setError('Please upload a PDF, HTML, or text file.');
      return;
    }

    // Create FormData for file upload
    const formData = new FormData();
    formData.append('file', file);
    formData.append('department_id', departmentId);

    setSaving(true);
    setError(null);

    try {
      const response = await axios.post('/api/conversation/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setError(null);
        setCurrentProcessingId(response.data.job_id);
        
        // Show success message with processing ID
        alert(`Document "${file.name}" uploaded successfully and queued for processing. Processing ID: ${response.data.job_id}`);
        
        // Clear the form
        setForm({ name: '', document_content: '' });
        setShowForm(false);
        
        // Refresh processing jobs
        fetchProcessingJobs();
      } else {
        throw new Error(response.data.error || 'Upload failed');
      }
    } catch (error: any) {
      console.error('Upload error:', error);
      setError(error.response?.data?.error || 'Failed to upload document. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await axios.post(`${API_BASE}/${departmentId}/documentation`, form);
      setShowForm(false);
      fetchDocs();
    } catch (e: any) {
      setError('Failed to save documentation.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-white rounded shadow p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">{departmentName} Documentation</h2>
      
      {/* Processing Jobs Section */}
      {processingJobs.length > 0 && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="text-lg font-medium mb-3 text-blue-900">Document Processing Status</h3>
          <div className="space-y-3">
            {processingJobs.map((job) => (
              <div key={job.job_id} className="bg-white p-3 rounded border">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-sm">{job.filename}</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    job.status === 'completed' ? 'bg-green-100 text-green-800' :
                    job.status === 'failed' ? 'bg-red-100 text-red-800' :
                    job.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {job.status}
                  </span>
                </div>
                
                {job.status === 'processing' && (
                  <div className="mb-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${job.progress}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-gray-600 mt-1">
                      {job.processing_details.processed_chunks} / {job.processing_details.total_chunks} chunks processed ({job.progress}%)
                    </div>
                  </div>
                )}
                
                {job.status === 'failed' && job.error_message && (
                  <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
                    Error: {job.error_message}
                  </div>
                )}
                
                <div className="text-xs text-gray-500">
                  Started: {job.started_at ? new Date(job.started_at).toLocaleString() : new Date(job.created_at).toLocaleString()} 
                  {job.elapsed_time > 0 && ` (${Math.round(job.elapsed_time)}s elapsed)`}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading ? (
        <div>Loading...</div>
      ) : error ? (
        <div className="text-red-500">{error}</div>
      ) : (
        <>
          <ul className="mb-4">
            {docs.length === 0 && <li className="text-gray-500">No documentation uploaded yet.</li>}
            {docs.map((doc, idx) => (
              <li key={doc.name} className="mb-2 border-b pb-2 flex justify-between items-center">
                <div>
                  <span className="font-medium">{doc.name}</span>
                  <p className="text-gray-700 whitespace-pre-line text-sm mt-1">{doc.document_content}</p>
                </div>
                <div>
                  <button className="text-blue-600 hover:underline mr-2" onClick={() => handleEdit(idx)}>Edit</button>
                  <button className="text-red-600 hover:underline" onClick={() => handleDelete(idx)}>Delete</button>
                </div>
              </li>
            ))}
          </ul>
          <button
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            onClick={handleAdd}
          >
            Add Document
          </button>
        </>
      )}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
          <div className="bg-white rounded shadow-lg p-6 w-full max-w-md relative">
            <button
              className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
              onClick={() => setShowForm(false)}
            >
              &times;
            </button>
            <h3 className="text-lg font-semibold mb-4">{editIndex !== null ? 'Edit' : 'Add'} Document</h3>
            <form onSubmit={handleFormSubmit}>
              <div className="mb-4">
                <label className="block mb-1 font-medium">Document Name</label>
                <input
                  type="text"
                  name="name"
                  value={form.name}
                  onChange={handleFormChange}
                  className="w-full border rounded px-3 py-2"
                  required
                  disabled={saving}
                />
              </div>

              <div className="mb-4">
                <label className="block mb-1 font-medium">Upload Document for Q&A</label>
                <input
                  type="file"
                  accept=".pdf,.html,.txt"
                  onChange={handleFileChange}
                  className="w-full border rounded px-3 py-2"
                  disabled={saving}
                />
                <div className="text-xs text-gray-600 mt-1">
                  Supported formats: PDF, HTML, TXT. Documents will be processed for AI-powered Q&A.
                </div>
                {saving && (
                  <div className="text-xs text-blue-600 mt-2 flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                    Processing document...
                  </div>
                )}
              </div>
              <button
                type="submit"
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DepartmentDocsManager;
