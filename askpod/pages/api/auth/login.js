export default async function handler(req, res) {
    if (req.method === "POST") {
      const response = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams(req.body)
      });
      const data = await response.json();
      res.status(response.status).json(data);
    } else {
      res.status(405).json({ message: "Method not allowed" });
    }
  }