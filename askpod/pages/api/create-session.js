import nookies from "nookies";

export default async function handler(req, res) {
  const cookies = nookies.get({ req });
  const token = cookies.token;

  try {
    const response = await fetch("http://localhost:8000/create_session", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify(req.body),
    });
    if (!response.ok) {
      throw new Error("Failed to create session");
    }
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: error.message || "Internal Server Error" });
  }
}