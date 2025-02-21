import axios from "axios";

export const config = {
  api: { bodyParser: false },
};

const handler = async (req, res) => {
  console.log("Received request:", req.method);
  
  if (req.method !== "POST") {
    console.log("Method not allowed:", req.method);
    return res.status(405).json({ message: "Method not allowed" });
  }

  try {
    const sessionId = req.query.session_id;
    if (!sessionId) {
      console.error("Missing session id");
      return res.status(400).json({ message: "Missing session id" });
    }
    
    const authHeader = req.headers.authorization;
    if (!authHeader) {
      console.error("Missing authorization header");
      return res.status(401).json({ message: "Missing authentication token" });
    }
    
    const headers = {
      "Content-Type": "application/json",
      Authorization: authHeader,
    };

    const payload = Number(sessionId);
    const endpointUrl = "http://localhost:8000/generate_podcast";
    console.log("Sending request to backend endpoint:", endpointUrl, "Payload:", payload);

    const response = await axios.post(endpointUrl, payload, { headers });
    console.log("Received response from backend. Podcast path:", response.data.podcast_path);
    return res.status(200).json({ podcast_path: response.data.podcast_path });
  } catch (error) {
    console.error("Error in handler:", error);
    return res.status(500).json({ message: error.message });
  }
};

export default handler;