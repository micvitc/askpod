import { IncomingForm } from "formidable";
import fs from "fs/promises"; // Use the promise-based fs module
import path from "path";
import fetch from "node-fetch";
import FormData from "form-data";
import { v4 as uuidv4 } from "uuid"; // Import UUID library
import { createReadStream } from "fs"; // Import createReadStream from fs module

export const config = {
  api: {
    bodyParser: false,
  },
};

const handler = async (req, res) => {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  let files;
  try {
    // Ensure uploads directory exists
    const uploadsDir = path.join(process.cwd(), "uploads");
    try {
      await fs.mkdir(uploadsDir, { recursive: true });
    } catch (err) {
      if (err.code !== "EEXIST") throw err;
    }

    // Parse incoming file
    const form = new IncomingForm({
      uploadDir: uploadsDir,
      keepExtensions: true,
      maxFileSize: 10 * 1024 * 1024, // 10MB limit
    });

    const [fields, allFiles] = await new Promise((resolve, reject) => {
      form.parse(req, (err, fields, files) => {
        if (err) reject(err);
        resolve([fields, files]);
      });
    });
    files = allFiles;

    const file = files.file?.[0] || files.file;
    if (!file || !file.filepath) {
      throw new Error("File not provided or could not be saved");
    }

    // Generate a unique file name without original extension
    const originalName = path.parse(file.originalFilename).name;
    const uniqueFileName = `${uuidv4()}-${originalName}`;
    
    // Send file to FastAPI
    const formData = new FormData();
    formData.append("file", createReadStream(file.filepath), {
      filename: uniqueFileName,
      contentType: file.mimetype
    });

    const response = await fetch("http://localhost:8000/generate_podcast", {
      method: "POST",
      body: formData,
      headers: formData.getHeaders()
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Error processing file");
    }

    // FastAPI returns { "podcast_path": "<URL to generated audio>" }
    const data = await response.json();
    console.log(data.podcast_path);

    // Simply return the backend provided URL to the frontend.
    return res.status(200).json({ podcast_path: data.podcast_path });

  } catch (error) {
    return res.status(500).json({ message: error.message });
  } finally {
    // Clean up the uploaded file
    if (files?.file) {
      const filePath = files.file?.[0]?.filepath || files.file?.filepath;
      if (filePath) {
        try {
          await fs.unlink(filePath);
        } catch (e) {
          console.error("Error cleaning up file:", e);
        }
      }
    }
  }
};

export default handler;