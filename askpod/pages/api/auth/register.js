export default async function handler(req, res) {
    if (req.method === "POST") {
      const { full_name, username, password } = req.body;
  
      try {
        const response = await fetch("http://localhost:8000/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ full_name, username, password }),
        });
  
        const data = await response.json();
  
        if (response.ok) {
          res.status(200).json(data);
        } else {
          res.status(response.status).json(data);
        }
      } catch (error) {
        res.status(500).json({ detail: "Internal Server Error" });
      }
    } else {
      res.setHeader("Allow", ["POST"]);
      res.status(405).end(`Method ${req.method} Not Allowed`);
    }
  }