"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function NewSession() {
  const [sessionId, setSessionId] = useState(null);
  const [pdfFile, setPdfFile] = useState(null);

  const createSession = async () => {
    try {
      const res = await fetch("/api/create-session", {
        method: "POST",
        credentials: "include",
      });
      if (!res.ok) {
        alert("Failed to create session");
        return;
      }
      const data = await res.json();
      setSessionId(data.id);
      alert(`Session ${data.id} created. Now select a PDF to upload.`);
    } catch (error) {
      console.error("Error creating session:", error);
    }
  };

  const handleFileChange = (e) => {
    setPdfFile(e.target.files[0]);
  };

  const uploadPdfToSession = async () => {
    if (!sessionId || !pdfFile) {
      alert("Please create a session and select a PDF file.");
      return;
    }
    try {
      const formData = new FormData();
      formData.append("file", pdfFile);

      const res = await fetch(`/api/upload-pdf-to-session?session_id=${sessionId}`, {
        method: "POST",
        credentials: "include",
        body: formData,
      });
      if (!res.ok) {
        alert("Failed to upload PDF");
        return;
      }
      const data = await res.json();
      console.log("PDF uploaded:", data);
      alert("PDF uploaded successfully!");
    } catch (error) {
      console.error("Error uploading PDF:", error);
    }
  };

  return (
    <Card className="my-4 p-4">
      <CardHeader>
        <CardTitle>Create New Session</CardTitle>
      </CardHeader>
      <CardContent>
        <Button onClick={createSession}>Create New Session</Button>
        {sessionId && (
          <div className="mt-4 flex items-center space-x-2">
            <Input type="file" accept=".pdf" onChange={handleFileChange} />
            <Button onClick={uploadPdfToSession}>Upload PDF</Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}