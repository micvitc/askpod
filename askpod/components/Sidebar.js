"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import nookies from "nookies";

export default function Sidebar() {
  const [sessions, setSessions] = useState([]);
  const [error, setError] = useState("");

  const fetchSessions = async () => {
    const token = nookies.get(null).token;
    try {
      const res = await fetch("/api/sessions", {
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

  const createSession = async () => {
    const token = nookies.get(null).token;
    try {
      const res = await fetch("/api/create-session", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          ...(token && { Authorization: `Bearer ${token}` }),
        },
      });
      if (!res.ok) throw new Error("Failed to create session");
      const newSession = await res.json();
      setSessions((prevSessions) => [...prevSessions, newSession]);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle>Your Sessions</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col gap-4">
        {error && (
          <div className="text-red-500 text-sm">
            Error: {error}
          </div>
        )}
        <Button onClick={createSession} className="w-full">
          Create Session
        </Button>
        
        <div className="flex-1 overflow-auto">
          {sessions.length === 0 ? (
            <p className="text-gray-600 text-sm">No sessions yet.</p>
          ) : (
            <ul className="space-y-3">
              {sessions.map((session) => (
                <li
                  key={session.id}
                  className="p-3 border rounded hover:bg-gray-100 transition-colors"
                >
                  <Link href={`/session/${session.id}`} className="block">
                    <div className="text-sm font-semibold">
                      {session.pdf_name || "Untitled"}
                    </div>
                    <Separator className="my-2" />
                    <div className="text-xs text-gray-500">
                      {new Date(session.created_at).toDateString()}
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </CardContent>
    </Card>
  );
}