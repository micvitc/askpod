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
    // Forward the incoming request body (which should be FormData) to FastAPI.
    // Note: In a pages API route, file uploads may require additional parsing.
    // Here we assume that body is correctly forwarded. If not, consider using a library like 'formidable'.
    const response = await fetch(
      `http://localhost:8000/upload_pdf_to_session?session_id=${session_id}`,
      {
        method: "POST",
        // Do not set Content-Type header when forwarding formData.
        body: req,
      }
    );

    if (!response.ok) {
      return res.status(500).json({ error: "Failed to upload PDF" });
    }
    const data = await response.json();
    return res.status(200).json(data);
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}