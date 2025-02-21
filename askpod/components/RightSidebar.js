import React, { useEffect, useState, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import nookies from "nookies";
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import { Loader2 } from "lucide-react";

export default function RightSidebar({ currentSessionId }) {
  const [sessions, setSessions] = useState([]);
  const [error, setError] = useState("");
  const [uploadFiles, setUploadFiles] = useState({});
  const [fileChosen, setFileChosen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const fileInputRef = useRef(null);

  const fetchSessions = async () => {
    const token = nookies.get(null).token;
    try {
      const res = await fetch("http://localhost:8000/sessions", {
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          ...(token && { Authorization: `Bearer ${token}` }),
        },
      });
      if (!res.ok) throw new Error("Failed to fetch sessions");
      const data = await res.json();
      setSessions(data);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleFileChange = (sessionId, file) => {
    setUploadFiles((prev) => ({ ...prev, [sessionId]: file }));
    setFileChosen(true);
  };

  const handleChooseFile = () => {
    fileInputRef.current?.click();
  };

  const uploadPDF = async (sessionId) => {
    const file = uploadFiles[sessionId];
    if (!file) {
      alert("Please select a PDF file to upload.");
      return;
    }
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`/api/upload-pdf-to-session?session_id=${sessionId}`, {
        method: "POST",
        credentials: "include",
        body: formData,
      });
      if (!res.ok) {
        alert("Failed to upload PDF");
        return;
      }
      await res.json();
      fetchSessions();
    } catch (error) {
      console.error("Error uploading PDF: ", error);
      alert("Error uploading PDF.");
    }
  };

  const generatePodcast = async (sessionId) => {
    const token = nookies.get(null).token;
    setIsGenerating(true);
    try {
      const headers = {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      };
      const res = await fetch(`/api/generate-podcast?session_id=${sessionId}`, {
        method: "POST",
        credentials: "include",
        headers,
      });
      if (!res.ok) {
        alert("Failed to generate podcast");
        return;
      }
      const updatedSession = await res.json();
      setSessions((prev) =>
        prev.map((s) => (s.id === sessionId ? updatedSession : s))
      );
    } catch (error) {
      console.error("Error generating podcast: ", error);
      alert("Error generating podcast.");
    } finally {
      setIsGenerating(false);
    }
  };

  const currentSession = sessions.find(
    (session) => session.id === currentSessionId
  );

  return (
    <Card className="h-full w-full flex flex-col">
      <CardHeader>
        <CardTitle>Session Controls</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto min-h-0">
        {error && <div className="p-2 text-red-500">{error}</div>}
        {!currentSession ? (
          <p>No current session found.</p>
        ) : (
          <div key={currentSession.id} className="border p-3 rounded">
            {currentSession.pdf_path && currentSession.pdf_path !== "" ? (
              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2">
                  <PictureAsPdfIcon className="w-6 h-6" />
                  <a href={currentSession.pdf_path} target="_blank" rel="noopener noreferrer">
                    {currentSession.pdf_name.split('/').pop()}
                  </a>
                </div>
                <Button
                  size="sm"
                  onClick={() => generatePodcast(currentSession.id)}
                  className="w-full mt-2"
                  disabled={isGenerating || currentSession.audio_path}
                >
                  {isGenerating ? <Loader2 className="animate-spin mr-2" /> : "Generate Podcast"}
                  {isGenerating && "Please wait"}
                </Button>
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                <input
                  type="file"
                  accept=".pdf"
                  ref={fileInputRef}
                  className="hidden"
                  onChange={(e) =>
                    handleFileChange(currentSession.id, e.target.files[0])
                  }
                />
                <Button
                  size="sm"
                  onClick={handleChooseFile}
                  className={`w-full ${fileChosen ? "bg-green-500" : ""}`}
                >
                  {fileChosen ? "File Chosen" : "Choose File"}
                </Button>
                <Button 
                  size="sm" 
                  onClick={() => uploadPDF(currentSession.id)} 
                  className="w-full mt-2"
                >
                  Upload PDF
                </Button>
              </div>
            )}
          </div>
        )}
      </CardContent>
      {currentSession && currentSession.audio_path && (
        <div className="mt-auto border-t bg-gray-100 p-3">
          <audio controls className="w-full rounded-lg shadow-md">
            <source src={currentSession.audio_path} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </Card>
  );
}