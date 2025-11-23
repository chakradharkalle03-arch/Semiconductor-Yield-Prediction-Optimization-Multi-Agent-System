// Simple Node.js/Express server for frontend
const express = require('express');
const path = require('path');
const cors = require('cors');
const axios = require('axios');
const multer = require('multer');

const app = express();
const PORT = 3008;
const BACKEND_URL = 'http://127.0.0.1:8006';

// Enable CORS
app.use(cors());

// Parse JSON bodies (but not multipart/form-data)
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Configure multer for file uploads (memory storage)
const upload = multer({ storage: multer.memoryStorage() });

// API proxy endpoint - must come before static files
app.all('/api/*', async (req, res) => {
  try {
    const apiPath = req.path.replace('/api', '');
    const isPdfEndpoint = apiPath.includes('/generate-report');
    const isUploadEndpoint = apiPath.includes('/datasets/upload');
    
    // Handle file uploads (multipart/form-data)
    if (isUploadEndpoint && req.method === 'POST') {
      upload.single('file')(req, res, async (err) => {
        if (err) {
          return res.status(400).json({ error: 'File upload error: ' + err.message });
        }
        
        try {
          const FormData = require('form-data');
          const formData = new FormData();
          
          // Add file if present
          if (req.file) {
            formData.append('file', req.file.buffer, {
              filename: req.file.originalname,
              contentType: req.file.mimetype
            });
          }
          
          // Add dataset_name (always send, even if empty)
          const datasetName = req.body?.dataset_name || '';
          formData.append('dataset_name', datasetName);
          
          const response = await axios({
            method: 'POST',
            url: `${BACKEND_URL}${apiPath}`,
            data: formData,
            headers: {
              ...formData.getHeaders()
            },
            maxContentLength: Infinity,
            maxBodyLength: Infinity
          });
          
          res.status(response.status).json(response.data);
        } catch (error) {
          console.error('Upload proxy error:', error.message);
          if (error.response) {
            const status = error.response.status;
            const data = error.response.data;
            if (typeof data === 'object') {
              res.status(status).json(data);
            } else {
              res.status(status).send(data);
            }
          } else {
            res.status(500).json({ error: error.message });
          }
        }
      });
      return; // Exit early for uploads
    }
    
    // Handle PDF downloads
    if (isPdfEndpoint) {
      const response = await axios({
        method: req.method,
        url: `${BACKEND_URL}${apiPath}`,
        data: req.body,
        headers: {
          'Content-Type': 'application/json',
        },
        responseType: 'arraybuffer'
      });
      
      // Forward PDF headers
      if (response.headers['content-type']) {
        res.setHeader('Content-Type', response.headers['content-type']);
      }
      if (response.headers['content-disposition']) {
        res.setHeader('Content-Disposition', response.headers['content-disposition']);
      }
      res.status(response.status).send(Buffer.from(response.data));
      return;
    }
    
    // Handle regular JSON requests
    const response = await axios({
      method: req.method,
      url: `${BACKEND_URL}${apiPath}`,
      data: req.body,
      headers: {
        'Content-Type': 'application/json',
      },
      responseType: 'json'
    });
    
    res.status(response.status).json(response.data);
    
  } catch (error) {
    console.error('API proxy error:', error.message);
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;
      const contentType = error.response.headers['content-type'] || '';
      
      if (contentType.includes('application/json') || typeof data === 'object') {
        res.status(status).json(data);
      } else {
        res.status(status).send(data);
      }
    } else {
      res.status(500).json({ error: error.message });
    }
  }
});

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Serve index.html for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, '127.0.0.1', () => {
  console.log(`✅ Frontend server running on http://127.0.0.1:${PORT}`);
  console.log(`📡 Backend API: ${BACKEND_URL}`);
  console.log(`🌐 Open http://localhost:${PORT} in your browser`);
  console.log(`🌐 Or http://127.0.0.1:${PORT}`);
}).on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`❌ Port ${PORT} is already in use. Please stop the other process.`);
  } else {
    console.error('❌ Server error:', err);
  }
  process.exit(1);
});

