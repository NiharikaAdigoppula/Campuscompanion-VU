const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Ensure upload directory exists
const uploadDir = './uploads';
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// Configure storage
const crypto = require('crypto');

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const subDir = req.uploadType || 'materials';
    const dir = path.join(uploadDir, subDir);
    
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    cb(null, dir);
  },
  filename: function (req, file, cb) {
    // Generate a cryptographically-secure random filename and preserve a safe extension
    const ext = path.extname(file.originalname).toLowerCase();

    // Whitelist of allowed extensions to avoid trusting user input
    const allowedExt = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.jpg', '.jpeg', '.png', '.gif'];
    const safeExt = allowedExt.includes(ext) ? ext : '.bin';

    const randomName = crypto.randomBytes(16).toString('hex');
    const filename = `${randomName}${safeExt}`;

    cb(null, filename);
  }
});

// File filter
const fileFilter = (req, file, cb) => {
  // Stronger checks: explicit extension and mimetype mapping
  const ext = path.extname(file.originalname).toLowerCase();

  const mimetypeMap = {
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.txt': 'text/plain',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif'
  };

  const expectedMime = mimetypeMap[ext];

  if (!expectedMime) {
    return cb(new Error('Invalid file extension.'));
  }

  // Some clients/OS may send slightly different mimetypes; check prefix for images
  if (expectedMime.startsWith('image/')) {
    if (!file.mimetype.startsWith('image/')) {
      return cb(new Error('Invalid image mimetype.'));
    }
  } else if (file.mimetype !== expectedMime) {
    return cb(new Error('Mimetype does not match file extension.'));
  }

  // Passed basic checks
  cb(null, true);
};

const upload = multer({
  storage: storage,
  limits: {
    fileSize: parseInt(process.env.MAX_FILE_SIZE) || 10 * 1024 * 1024 // 10MB default
  },
  fileFilter: fileFilter
});

module.exports = upload;
