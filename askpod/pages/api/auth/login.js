import axios from "axios";

export default async function handler(req, res) {
  if (req.method === "POST") {
    try {
      const params = new URLSearchParams(req.body);
      const response = await axios.post("http://localhost:8000/login", params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      res.status(response.status).json(response.data);
    } catch (error) {
      if (error.response) {
        res.status(error.response.status).json(error.response.data);
      } else {
        res.status(500).json({ message: error.message });
      }
    }
  } else {
    res.status(405).json({ message: "Method not allowed" });
  }
}