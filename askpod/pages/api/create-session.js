import nookies from "nookies";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  try {
    const response = await fetch("http://localhost:8000/create_session", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${nookies.get({ req }).token}`,
      },
      // You may need to forward cookies manually if required.
    });

    if (!response.ok) {
      return res.status(500).json({ error: "Failed to create session" });
    }
    const data = await response.json();
    return res.status(200).json(data);
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}