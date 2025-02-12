import { IncomingForm } from "formidable";
import fs from "fs";
import path from "path";
import fetch from "node-fetch";
import FormData from "form-data";

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
    if (!fs.existsSync(uploadsDir)) {
      fs.mkdirSync(uploadsDir, { recursive: true });
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

    // Send file to FastAPI
    const formData = new FormData();
    formData.append("file", fs.createReadStream(file.filepath), {
      filename: file.originalFilename,
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

    // Fetch the audio from the returned URL
    const audioResponse = await fetch(data.podcast_path);
    if (!audioResponse.ok) {
      throw new Error("Failed to retrieve generated audio");
    }
    const audioBuffer = await audioResponse.arrayBuffer();

    // Save locally to /public/audio/podcast.wav in Next.js
    const publicAudioDir = path.join(process.cwd(), "public", "audio");
    if (!fs.existsSync(publicAudioDir)) {
      fs.mkdirSync(publicAudioDir, { recursive: true });
    }
    const localFilePath = path.join(publicAudioDir, "podcast.wav");
    fs.writeFileSync(localFilePath, Buffer.from(audioBuffer));

    // Return local URL to frontend
    return res.status(200).json({ podcast_path: "/audio/podcast.wav" });

  } catch (error) {
    return res.status(500).json({ message: error.message });
  } finally {
    // Clean up the uploaded file
    if (files?.file) {
      const filePath = files.file?.[0]?.filepath || files.file?.filepath;
      if (filePath) {
        try {
          fs.unlinkSync(filePath);
        } catch (e) {
          console.error("Error cleaning up file:", e);
        }
      }
    }
  }
};

export default handler;