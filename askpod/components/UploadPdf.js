"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import nookies from "nookies";

const UploadPdf = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState("");
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError("");
    setAudioUrl("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const token = nookies.get(null).token;
      const response = await fetch("/api/generatePodcast", {
        method: "POST",
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
        },
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "An error occurred while processing the file.");
      }
      const data = await response.json();
      // Use the backend provided URL directly for the audio source
      setAudioUrl(data.podcast_path);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="file" className="block text-sm font-medium text-gray-700">
            Upload your PDF file
          </label>
          <input
            id="file"
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            className="mt-1 block w-full"
          />
        </div>
        <Button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Generate Podcast"}
        </Button>
      </form>

      {audioUrl && (
        <div className="mt-4 p-4 border rounded bg-green-50">
          <h2 className="text-lg font-bold">Generated Podcast</h2>
          <audio controls src={audioUrl} className="w-full mt-2">
            Your browser does not support the audio element.
          </audio>
        </div>
      )}

      {error && (
        <div className="mt-4 p-4 border rounded bg-red-50 text-red-700">
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
};

export default UploadPdf;