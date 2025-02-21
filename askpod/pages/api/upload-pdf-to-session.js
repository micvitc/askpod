import fs from "fs";
import formidable from "formidable";
import nookies from "nookies";
import FormData from "form-data";
import axios from "axios";

export const config = {
  api: {
    bodyParser: false,
  },
};

function parseForm(req) {
  return new Promise((resolve, reject) => {
    const form = formidable();
    form.parse(req, (err, fields, files) => {
      if (err) {
        return reject(err);
      }
      resolve({ fields, files });
    });
  });
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  const { session_id } = req.query;
  if (!session_id) {
    return res.status(400).json({ error: "Missing session_id" });
  }

  try {
    const { files } = await parseForm(req);
    if (!files.file) {
      return res.status(400).json({ error: "No file uploaded" });
    }
    const uploadedFile = Array.isArray(files.file) ? files.file[0] : files.file;
    
    const formData = new FormData();
    const filePath = uploadedFile.filepath || uploadedFile.path;
    formData.append("file", fs.createReadStream(filePath), uploadedFile.originalFilename);
    
    const token = nookies.get({ req }).token || "";
    const formHeaders = formData.getHeaders();
    
    const headers = {
      ...formHeaders,
      Authorization: `Bearer ${token}`,
    };
    delete headers["content-type"];
    
    const backendUrl = `http://localhost:8000/upload_pdf_to_session?session_id=${session_id}`;
    
    const response = await axios.post(backendUrl, formData, { headers });
    
    return res.status(200).json(response.data);
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}