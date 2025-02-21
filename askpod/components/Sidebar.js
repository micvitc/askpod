"use client";

import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import nookies from "nookies";
import NewSession from "./NewSession";

export default function Sidebar() {
  const [sessions, setSessions] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = nookies.get(null).token;
    fetch("http://localhost:8000/sessions", {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch sessions");
        return res.json();
      })
      .then((data) => setSessions(data))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="h-full w-full">
      <NewSession />
      <Card className="h-full">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg">Your Sessions</CardTitle>
        </CardHeader>
        <CardContent className="overflow-y-auto">
          {error && (
            <div className="p-2 text-red-500 text-sm">
              Error: {error}
            </div>
          )}
          {sessions.length === 0 ? (
            <p className="text-gray-600 text-sm">No sessions yet.</p>
          ) : (
            <ul className="space-y-3">
              {sessions.map((session) => (
                <li
                  key={session.id}
                  className="p-3 border rounded hover:bg-gray-100 transition-colors"
                >
                  <a
                    href={session.audio_path}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <div className="text-sm font-semibold">
                      {new Date(session.created_at).toLocaleString()}
                    </div>
                    <Separator className="my-2" />
                    <div className="text-xs text-gray-500">
                      PDF: {session.pdf_path.split("/").pop()}
                    </div>
                  </a>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}