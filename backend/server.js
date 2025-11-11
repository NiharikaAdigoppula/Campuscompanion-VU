// server.js
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const app = express();

// ===============================
// 🔐 Middleware Setup
// ===============================
app.use(helmet());
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan('dev'));

// ===============================
// ⚙️ Rate Limiting
// ===============================
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 1000, // limit each IP to 1000 requests per window (increased for development)
});
app.use('/api/', limiter);

// ===============================
// 🗂 Static Files (Uploads)
// ===============================
app.use('/uploads', express.static('uploads'));

// ===============================
// 📁 Enhanced File Serving for Materials
// ===============================
app.get('/uploads/materials/:filename', (req, res) => {
  const path = require('path');
  const fs = require('fs');
  
  const filename = req.params.filename;
  const filePath = path.join(__dirname, 'uploads', 'materials', filename);
  
  // Check if file exists
  if (!fs.existsSync(filePath)) {
    return res.status(404).json({
      success: false,
      message: 'File not found'
    });
  }
  
  // Get file extension and set appropriate content type
  const ext = path.extname(filename).toLowerCase();
  let contentType = 'application/octet-stream';
  
  switch (ext) {
    case '.pdf':
      contentType = 'application/pdf';
      break;
    case '.ppt':
      contentType = 'application/vnd.ms-powerpoint';
      break;
    case '.pptx':
      contentType = 'application/vnd.openxmlformats-officedocument.presentationml.presentation';
      break;
    case '.doc':
      contentType = 'application/msword';
      break;
    case '.docx':
      contentType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      break;
    case '.txt':
      contentType = 'text/plain';
      break;
    case '.jpg':
    case '.jpeg':
      contentType = 'image/jpeg';
      break;
    case '.png':
      contentType = 'image/png';
      break;
  }
  
  res.setHeader('Content-Type', contentType);
  res.setHeader('Content-Disposition', `inline; filename="${filename}"`);
  res.sendFile(filePath);
});

// ===============================
// 🧭 Routes Setup with Validation
// ===============================
const routes = [
  'auth',
  'admin',
  'timetable',
  'courses',
  'materials',
  'faculty',
  'chatbot',
  'events',
  'navigation',
  'helpdesk',
  'voiceChat',
  'pythonAgents',  // ⭐ NEW: Python AI Service Integration
  // Legacy routes (deprecated, use pythonAgents instead):
  'agenticAI',
  'agenticFeatures',
  'adminAgenticFeatures',
  'adminAgentic'
];

routes.forEach(route => {
  try {
    const router = require(`./routes/${route}`);
    if (typeof router !== 'function') {
      console.error(`❌ Route "${route}" is invalid — got type: ${typeof router}`);
    } else {
      app.use(`/api/${route}`, router);
      console.log(`✅ Loaded route: ${route}`);
    }
  } catch (err) {
    console.error(`💥 Error loading route "${route}":`, err.message);
  }
});

// ===============================
// 🩺 Health Check
// ===============================
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'CampusCompanion API is running' });
});

// ===============================
// ⚠️ Error Handling Middleware
// ===============================
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    success: false,
    message: err.message || 'Internal Server Error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

// ===============================
// 🚫 404 Handler
// ===============================
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: 'Route not found'
  });
});

// ===============================
// 💾 MongoDB Connection
// ===============================
const PORT = process.env.PORT || 5000;
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/campus-companion';

mongoose.connect(MONGODB_URI)
  .then(() => {
    console.log('✅ MongoDB connected successfully');

    // free the port if already used
    const server = app.listen(PORT, () => {
      console.log(`🚀 Server running on port ${PORT}`);
      console.log(`📍 Environment: ${process.env.NODE_ENV || 'development'}`);
    });

    // graceful error for EADDRINUSE
    server.on('error', err => {
      if (err.code === 'EADDRINUSE') {
        console.error(`❌ Port ${PORT} is already in use. Try freeing it or using another port.`);
      } else {
        console.error('Server Error:', err);
      }
    });
  })
  .catch((err) => {
    console.error('❌ MongoDB connection error:', err);
    process.exit(1);
  });

module.exports = app;

